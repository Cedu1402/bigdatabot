import multiprocessing
import pickle
import random
from datetime import timedelta
from multiprocessing import shared_memory

import numpy as np
import pandas as pd
from flask.cli import load_dotenv
from matplotlib import pyplot as plt
from tqdm import tqdm

from constants import TOKEN_COLUMN, PRICE_COLUMN, TRADING_MINUTE_COLUMN, PRICE_PCT_CHANGE
from data.cache_data import read_cache_data, save_cache_data
from data.data_split import get_index_of_similar_price
from database.token_sample_table import get_all_samples

cum_change = 'cumulative_pct_change'
log_return = 'log_return'
age_column = 'age'


def plot_simulations(true_price_change, sample_cut):
    # Extract the real price change
    real_price_path = true_price_change[cum_change].values

    # Extract the simulated paths (reshaped for plotting)
    simulated_paths = sample_cut.groupby(TOKEN_COLUMN)[cum_change].apply(list).tolist()

    # Plot all simulations
    plt.figure(figsize=(12, 6))
    for path in simulated_paths:
        plt.plot(path, color='gray', alpha=0.2)  # Light color for simulations

    # Highlight the real price path
    plt.plot(real_price_path, color='red', linewidth=2, label="Real Price Path")

    plt.xlabel("Time Steps (Minutes)")
    plt.ylabel("Cumulative % Change")
    plt.title("Monte Carlo Simulations vs. Real Price Path")
    plt.legend()
    plt.show()


def prepare_data(min_price_reached):
    prepared_data = read_cache_data('prep_full')
    if prepared_data is not None:
        token_list, data, min_trading_minutes = prepared_data
        return token_list, data, min_trading_minutes

    data = read_cache_data('token_samples_full')
    if data is None:
        token_samples = get_all_samples()
        data = pd.DataFrame()
        for sample in token_samples:
            data = pd.concat([data, sample.raw_data], ignore_index=True)

        data.reset_index(drop=True, inplace=True)
        data.sort_values(by=[TOKEN_COLUMN, TRADING_MINUTE_COLUMN], inplace=True)

    data[PRICE_PCT_CHANGE] = data.groupby(TOKEN_COLUMN)[PRICE_COLUMN].pct_change()
    data[log_return] = np.log1p(data[PRICE_PCT_CHANGE])

    # Calculate the minimum trading minute for each token group
    data[age_column] = data.groupby(TOKEN_COLUMN)[TRADING_MINUTE_COLUMN].transform('min')

    # Calculate the age per token (difference from the token's first trading minute)
    data[age_column] = (
            (data[TRADING_MINUTE_COLUMN] - data[age_column]).dt.total_seconds() // 3600).astype(
        int)

    filtered_data = data.copy()
    filtered_data = filtered_data[filtered_data[age_column] <= 5]

    filtered_data = filtered_data.groupby(TOKEN_COLUMN).filter(
        lambda group: group[PRICE_COLUMN].max() > min_price_reached
    )

    two_k_data = filtered_data[filtered_data[PRICE_COLUMN] >= min_price_reached]
    min_trading_minutes = two_k_data.groupby(TOKEN_COLUMN)[TRADING_MINUTE_COLUMN].min()

    # for each token loop trough each step and load x random tokens
    token_list = filtered_data[TOKEN_COLUMN].unique()

    save_cache_data('prep_full', (token_list, data, min_trading_minutes))

    return token_list, data, min_trading_minutes


def run_token(token, min_trading_minutes, random_points_of_token_life, token_list, sample_amount, shm_name):
    # get min the token reached required mc.
    existing_shm = shared_memory.SharedMemory(name=shm_name)
    data = pickle.loads(bytes(existing_shm.buf))

    mc_reached_min = min_trading_minutes[token]
    current_row = data[(data[TOKEN_COLUMN] == token) & (data[TRADING_MINUTE_COLUMN] == mc_reached_min)]
    current_age = current_row[age_column].iloc[0]

    time_series = [mc_reached_min + timedelta(minutes=i) for i in range(300 - current_age)]
    sampled_minutes = random.sample(time_series, random_points_of_token_life)
    result_data = list()

    for trading_min in sampled_minutes:
        current_row = data[(data[TOKEN_COLUMN] == token) & (data[TRADING_MINUTE_COLUMN] == trading_min)]
        if len(current_row) == 0:
            continue
        current_price = current_row[PRICE_COLUMN].iloc[0]
        current_age = current_row[age_column].iloc[0]

        sample_tokens = np.array(random.sample(list(token_list[token_list != token]), sample_amount))
        same_price_tokens = random.sample(list(sample_tokens), sample_amount // 2)
        same_age_tokens = list(token_list[~np.isin(token_list, same_price_tokens)])

        token_price_data = data[data[TOKEN_COLUMN].isin(sample_tokens)]

        # sample tokens with same mc as current
        same_price_token_data = token_price_data[token_price_data[TOKEN_COLUMN].isin(same_price_tokens)]
        index_of_similar_price = get_index_of_similar_price(same_price_token_data, current_price)
        same_price_cut = same_price_token_data.groupby(TOKEN_COLUMN, group_keys=False).apply(
            lambda group: group.loc[index_of_similar_price[group.name]: index_of_similar_price[group.name] + 299]
        )

        # sample tokens at same age as current
        same_age_token_data = token_price_data[token_price_data[TOKEN_COLUMN].isin(same_age_tokens)]
        same_age_cut = same_age_token_data.groupby(TOKEN_COLUMN, group_keys=False).apply(
            lambda group: group[group[age_column] > current_age].head(300)
        )

        sample_data = pd.concat([same_price_cut, same_age_cut], ignore_index=True)
        # for sample tokens take the same cut of data
        sample_data[cum_change] = sample_data.groupby(TOKEN_COLUMN)[log_return].cumsum()
        row = {
            TOKEN_COLUMN: token,
            TRADING_MINUTE_COLUMN: mc_reached_min,
            'volatility': sample_data[cum_change].std(),
            'skew': sample_data[cum_change].skew(),
            'kurt': sample_data[cum_change].kurtosis(),
            'crash_prob': (sample_data[cum_change] < -0.5).mean(),
            'moon_prob': (sample_data[cum_change] > 0.5).mean(),
            'mean_max_return': sample_data.groupby(TOKEN_COLUMN)[cum_change].max().mean(),
            'median_max_return': sample_data.groupby(TOKEN_COLUMN)[cum_change].max().median()
        }
        result_data.append(row)
    print("Finished token")
    return result_data


def main():
    print("Start dataset creation")
    min_price_reached = 0.0001
    token_list, data, min_trading_minutes = prepare_data(min_price_reached)
    data.reset_index(drop=True, inplace=True)

    data_bytes = pickle.dumps(data)
    shm = shared_memory.SharedMemory(create=True, size=len(data_bytes))
    shm.buf[:len(data_bytes)] = data_bytes  # Copy data

    sample_amount = 5000
    random_points_of_token_life = 5

    tasks = [(token, min_trading_minutes,
              random_points_of_token_life, token_list, sample_amount, shm.name) for token in token_list]

    with multiprocessing.Pool(processes=2) as pool:
        results = list(tqdm(pool.starmap(run_token, tasks), total=len(tasks)))
        results = [item for result in results for item in result if item is not None]

        save_cache_data('simulations', pd.DataFrame(results))


if __name__ == '__main__':
    load_dotenv()
    main()

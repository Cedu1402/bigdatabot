import multiprocessing
import random
from datetime import datetime
from typing import List

import pandas as pd
from matplotlib import pyplot as plt

from constants import TRADING_MINUTE_COLUMN, TOKEN_COLUMN, PRICE_COLUMN, RANDOM_SEED, AGE_IN_MINUTES_COLUMN, \
    CURRENT_ASSET_PRICE_COLUMN, PRICE_PCT_CHANGE
from data.random_seed import set_random_seed
from mcts.action import TradeAction
from mcts.info_set import InfoSet
from mcts.price_smapling import jump_diffusion
from mcts.token_sample import load_token_ohlcv_data
from mcts.trades import run_buy_action, run_sell_action
from mcts.tree import MonteCarloSearchTree


def get_validation_tokens(data: pd.DataFrame, amount: int) -> List[pd.DataFrame]:
    max_date = datetime(2024, 11, 30)
    min_date = datetime(2024, 11, 25)

    possible_tokens = list(data[(data[TRADING_MINUTE_COLUMN] < max_date) & (data[TRADING_MINUTE_COLUMN] >= min_date)][
                               TOKEN_COLUMN].unique())

    selected_tokens = random.sample(possible_tokens, amount if len(possible_tokens) > amount else len(possible_tokens))

    print("Amount of tokens selected:", len(selected_tokens))
    return [group for _, group in data[data[TOKEN_COLUMN].isin(selected_tokens)].groupby(TOKEN_COLUMN)]


def remove_non_traded_rows(token_data: pd.DataFrame, trades: pd.DataFrame, token: str) -> pd.DataFrame:
    token_min_trading_minute = trades[trades[TOKEN_COLUMN] == token][TRADING_MINUTE_COLUMN].min()
    return token_data[token_data[TRADING_MINUTE_COLUMN] >= token_min_trading_minute]


def filter_info_sets_by_token_age(data: pd.DataFrame, token_age: int):
    return data[data[AGE_IN_MINUTES_COLUMN] >= token_age]


def apply_cumulative_price_change_by_token(df: pd.DataFrame, base_price: float) -> pd.DataFrame:
    # Group by the token column and calculate the cumulative percentage change
    df['cumulative_pct_change'] = df.groupby(TOKEN_COLUMN)[PRICE_PCT_CHANGE].transform(
        lambda x: (1 + x / 100).cumprod()) # Todo fix this!

    # Apply the cumulative percentage change to the base price
    df[CURRENT_ASSET_PRICE_COLUMN] = base_price * df['cumulative_pct_change']

    # Drop the intermediate column used for the calculation
    return df.drop(columns=['cumulative_pct_change'])


def plot_info_sets(info_sets):
    plt.figure(figsize=(12, 6))
    for info_set in info_sets:
        plt.plot(info_set[CURRENT_ASSET_PRICE_COLUMN], linewidth=1)
    plt.title("Possible Price Movements (Jump-Diffusion Model)")
    plt.xlabel("Timesteps")
    plt.ylabel("Price (USDC)")
    plt.show()


def run_token_evaluation(token_data, trade_data, ohlcv_data):
    token = token_data[TOKEN_COLUMN].iloc[0]
    token_data = remove_non_traded_rows(token_data, trade_data, token)
    # token_start_date = token_data[TRADING_MINUTE_COLUMN].min()

    current_holding = 0
    current_step = 0
    last_action = TradeAction.DO_NOTHING

    # info_sets_data = sample_random_tokens(token, ohlcv_data, 50, token_start_date)

    investment_amount = 10
    info_set = InfoSet()
    buy_price = None
    sell_price = None

    for index, row in token_data.iterrows():
        token_price = row[PRICE_COLUMN]

        # current_info_sets_data = filter_info_sets_by_token_age(info_sets_data.copy(), row[AGE_IN_MINUTES_COLUMN])
        # current_info_sets_data = apply_cumulative_price_change_by_token(current_info_sets_data, token_price)
        # info_sets = get_info_sets(current_info_sets_data)
        info_sets = list()
        for i in range(500):
            info_sets.append(jump_diffusion(token_price, timesteps=600))

        # plot_info_sets(info_sets)
        info_set.set_info_set(info_sets)

        current_step += 1
        mcts = MonteCarloSearchTree(investment_amount, current_holding, current_step, last_action)
        mcts.evaluate_tree(5)
        for child in mcts.root.children:
            print(child.state.action, child.visit_count, child.reward_value)

        print("Tree depth:", mcts.get_depth())
        if len(mcts.root.children) == 0:
            return 0

        best_child = max(mcts.root.children, key=lambda x: x.visit_count)
        last_action = best_child.state.action

        if last_action == TradeAction.BUY and best_child.reward_value > 0:
            current_holding = run_buy_action(investment_amount, token_price * 1.15)  # simulate 15% slippage
            buy_price = token_price * 1.15
        elif last_action == TradeAction.BUY and best_child.reward_value < 0:
            last_action = TradeAction.DO_NOTHING
        elif last_action == TradeAction.SELL:
            return_of_investment = run_sell_action(current_holding, token_price) - investment_amount
            sell_price = token_price
            print("Return of investment:", return_of_investment, buy_price, token_price)
            plt.figure(figsize=(12, 6))
            plt.plot(token_data[PRICE_COLUMN], label="Token Price")
            plt.title("Token Price Evolution During Evaluation")
            plt.xlabel("Steps")
            plt.ylabel("Price (USDC)")
            plt.axhline(buy_price, color='blue', linestyle='--', label=f"Buy Price: {buy_price:.2f}")
            plt.axhline(sell_price, color='red', linestyle='--', label=f"Sell Price: {sell_price:.2f}")

            plt.legend()
            plt.show()
            return return_of_investment

    return 0


def run_mcts_on_validation():
    ohlcv_data, trade_data = load_token_ohlcv_data()
    validation_tokens = get_validation_tokens(ohlcv_data, 21)
    print("Proceses", multiprocessing.cpu_count() - 1)
    with multiprocessing.Pool(processes=1) as pool:
        results = pool.starmap(run_token_evaluation,
                               [(token_data, trade_data, ohlcv_data) for token_data in validation_tokens])

    pool.close()
    pool.join()

    # Sum up all the results from the different processes
    total_return = sum(results)
    print(f"Total return: $ {total_return}")


if __name__ == '__main__':
    set_random_seed(RANDOM_SEED)
    run_mcts_on_validation()

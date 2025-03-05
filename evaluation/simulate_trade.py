from typing import List

import pandas as pd

from cache_helper import get_cache_file_data
from constants import INVESTMENT_AMOUNT, TOKEN_COLUMN, TOKEN_CLOSE_VOLUME_1M_QUERY, PRICE_COLUMN, TRADING_MINUTE_COLUMN


def do_ranges_overlap(start1, end1, start2, end2):
    """
    Checks if two date ranges overlap.
    """

    return start1 <= end2 and start2 <= end1


def get_max_concurrent_tokens(buy_sell_times: List[dict]):
    max_overlap = 0
    for i in range(len(buy_sell_times)):
        overlap_counter = 0
        for y in range(len(buy_sell_times)):
            if y == i:
                continue
            if do_ranges_overlap(buy_sell_times[i]['buy'], buy_sell_times[i]['sell'], buy_sell_times[y]['buy'],
                                 buy_sell_times[y]['sell']):
                overlap_counter += 1

        if overlap_counter >= max_overlap:
            max_overlap = overlap_counter
    return max_overlap


def get_list_of_time_between_dates(buy_sell_times: List[dict], end_key: str):
    hodel_time = list()
    for item in buy_sell_times:
        hodel_time.append(abs((item['buy'] - item[end_key]).total_seconds()) / 60)

    return hodel_time


def get_hold_time(buy_sell_times: List[dict]) -> List[float]:
    return get_list_of_time_between_dates(buy_sell_times, 'sell')


def get_max_hold_time(buy_sell_times: List[dict]) -> List[float]:
    return get_list_of_time_between_dates(buy_sell_times, 'max_sell')


def get_sell_time(token_price_data, token, data, label, win_percentage, draw_down_percentage):
    try:
        if label:
            filtered_data = token_price_data[
                (token_price_data[TOKEN_COLUMN] == token) &
                (token_price_data[TRADING_MINUTE_COLUMN] > data[TRADING_MINUTE_COLUMN]) &
                (token_price_data[PRICE_COLUMN] >= data[PRICE_COLUMN] * (1 + win_percentage / 100))]
        else:
            filtered_data = token_price_data[
                (token_price_data[TOKEN_COLUMN] == token) &
                (token_price_data[TRADING_MINUTE_COLUMN] > data[TRADING_MINUTE_COLUMN]) &
                (token_price_data[PRICE_COLUMN] >= data[PRICE_COLUMN] * (1 - (
                        draw_down_percentage / 100)))]

        return filtered_data[TRADING_MINUTE_COLUMN].iloc[0], filtered_data[TRADING_MINUTE_COLUMN].iloc[-1]
    except Exception as e:
        print(e)


def run_simulation(val_x: pd.DataFrame, val_y: List[bool], prediction: List[bool], config: dict):
    ape_amount = INVESTMENT_AMOUNT
    total_return = 0
    token_bought = list()
    good_trades = 0
    bad_trades = 0

    # todo save this with train data as this is a point where we will run into missmatches sooner or later!!!
    token_price_data = get_cache_file_data(TOKEN_CLOSE_VOLUME_1M_QUERY)
    win_percentage = config["win_percentage"]
    draw_down_percentage = config["draw_down_percentage"]
    draw_down_percentage = draw_down_percentage if draw_down_percentage != "infinite" else 100

    val_x.reset_index(drop=True, inplace=True)
    token_ages = list()
    token_market_caps = list()
    token_buy_sell_times = list()
    tokens = val_x[TOKEN_COLUMN].unique().tolist()
    good_tokens = set()

    for index, data in val_x.iterrows():

        if val_y[index]:
            good_tokens.add(data[TOKEN_COLUMN])

        if not prediction[index]:
            continue

        token = data[TOKEN_COLUMN]

        if token not in token_bought:
            # token_ages.append(data[AGE_IN_MINUTES_COLUMN])
            # token_market_caps.append(data[MARKET_CAP_USD])
            # if data[MARKET_CAP_USD] == 0:
            #     print("yes")
            token_bought.append(token)
            # sell_time, max_sell_time = get_sell_time(token_price_data, token, data, val_y[index], win_percentage,
            #                                          draw_down_percentage)
            #
            # token_buy_sell_times.append({'buy': data[TRADING_MINUTE_COLUMN],
            #                              'sell': sell_time, 'max_sell': max_sell_time})

            if val_y[index]:
                total_return += ape_amount * (win_percentage / 100)
                good_trades += 1
            else:
                total_return += -(ape_amount * (draw_down_percentage / 100))
                bad_trades += 1

    print("*" * 50)
    print(f"Validation tokens {len(tokens)}")
    print(f"Max good trades possible {len(good_tokens)}")
    print(f"Total return: {total_return}, Good trades: {good_trades}, Bad trades: {bad_trades}")
    print("*" * 50)

    # save_histogram(token_ages, 'Token Age', 'Age', 'Tokens', 'token_age.png', len(token_ages))
    # print_statistics(token_ages, "Token Age")
    #
    # save_histogram(token_market_caps, 'Market Cap', 'Market Cap', 'Tokens', 'market_cap.png', 50)
    # print_statistics(token_market_caps, "Market Cap")
    #
    # hodel_time = get_hold_time(token_buy_sell_times)
    # save_histogram(hodel_time, 'Hodel Time', 'Time', 'Tokens', 'hodel_time.png', 50)
    # print_statistics(hodel_time, "Hodel Time")
    #
    # max_hodel_time = get_max_hold_time(token_buy_sell_times)
    # print(f"Max Hodel is two min {len([0 for item in max_hodel_time if item <= 2])}")
    # save_histogram(max_hodel_time, 'Max Hodel Time', 'Time', 'Tokens', 'max_hodel_time.png', 50)
    # print_statistics(max_hodel_time, "Max Hodel Time")

    print(f"Max simultaneous Trades {get_max_concurrent_tokens(token_buy_sell_times)}")

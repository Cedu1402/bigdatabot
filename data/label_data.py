from typing import List

import pandas as pd

from constants import PRICE_COLUMN, TRADING_MINUTE_COLUMN, LABEL_COLUMN, TOKEN_COlUMN
from log import logger


def label_window(full_token_data: pd.DataFrame, window_data: pd.DataFrame,
                 win_percentage: int, draw_down_percentage: int) -> bool:
    last_price = window_data.iloc[-1][PRICE_COLUMN]
    last_minute = window_data.iloc[-1][TRADING_MINUTE_COLUMN]

    win_price = last_price * (1 + win_percentage / 100)
    lost_price = last_price * (1 - draw_down_percentage / 100)

    # Filter rows where the minute is greater than the last minute
    future_data = full_token_data[full_token_data[TRADING_MINUTE_COLUMN] > last_minute]

    # Find first row where price >= win_price
    win_index = future_data[future_data[PRICE_COLUMN] >= win_price].index.min()
    # Find first row where price <= lost_price
    draw_down_index = future_data[future_data[PRICE_COLUMN] <= lost_price].index.min()

    if pd.isna(win_index) and pd.isna(draw_down_index):
        return False  # Neither condition was met

    # Decide based on which event happened first
    if pd.notna(win_index) and (pd.isna(draw_down_index) or win_index < draw_down_index):
        return True  # Win condition met
    elif pd.notna(draw_down_index) and (pd.isna(win_index) or draw_down_index < win_index):
        return False  # Drawdown condition met


def label_data(split_data: List[pd.DataFrame], full_data: pd.DataFrame,
               win_percentage: int, draw_down_percentage: int) -> List[pd.DataFrame]:
    #  for each item check if when buy at close price we can make a *x
    #  with a max draw down of x %
    for item in split_data:
        token = item.iloc[0][TOKEN_COlUMN]
        full_token_data = full_data[full_data[TOKEN_COlUMN] == token]
        label = label_window(full_token_data, item, win_percentage, draw_down_percentage)
        item[LABEL_COLUMN] = label

    amount_of_true = len([1 for item in split_data if item[LABEL_COLUMN].iloc[0]])
    amount_of_false = len([1 for item in split_data if not item[LABEL_COLUMN].iloc[0]])

    logger.info("Amount of true windows: %s, Amount of false windows: %s", amount_of_true, amount_of_false)

    return split_data

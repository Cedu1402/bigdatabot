from typing import List

import pandas as pd

from constants import PRICE_COLUMN, TRADING_MINUTE_COLUMN, LABEL_COLUMN, TOKEN_COlUMN
from log import logger

WIN_PRICE = "win_price"
DRAW_DOWN_PRICE = "drawdown_price"
MIN_VALUE_COLUMN = 'min_value'
MIN_INDEX_COLUMN = 'min_index'
MAX_VALUE_COLUMN = 'max_value'
MAX_INDEX_COLUMN = 'max_index'


def get_min_max_with_indices_grouped(data: pd.DataFrame, x, token_column):
    # Group by the token column and apply the rolling calculation
    result = data.groupby(token_column).apply(
        lambda group: get_min_max_with_indices(group[PRICE_COLUMN], x), include_groups=False
    ).reset_index(drop=True)

    return result['min_value'], result['min_index'], result['max_value'], result['max_index']


def get_min_max_with_indices(series, x):
    # Reverse the series to simulate forward-looking window
    reversed_series = series.shift(-1).iloc[::-1]

    # Apply rolling window on the reversed series
    min_value = reversed_series.rolling(window=x, min_periods=x).apply(lambda window: window.min(), raw=False).iloc[
                ::-1]
    max_value = reversed_series.rolling(window=x, min_periods=x).apply(lambda window: window.max(), raw=False).iloc[
                ::-1]

    # Find the index of the min and max values (use reversed series)
    min_index = reversed_series.rolling(window=x, min_periods=x).apply(lambda window: window.idxmin(), raw=False).iloc[
                ::-1] + 1
    max_index = reversed_series.rolling(window=x, min_periods=x).apply(lambda window: window.idxmax(), raw=False).iloc[
                ::-1] + 1

    return pd.DataFrame({
        'min_value': min_value,
        'min_index': min_index,
        'max_value': max_value,
        'max_index': max_index
    })


def label_dataset(data: pd.DataFrame, win_percentage: int,
                  draw_down_percentage: int, max_trading_time: int) -> pd.DataFrame:
    # Sort by token and trading minute
    data = data.sort_values(by=[TOKEN_COlUMN, TRADING_MINUTE_COLUMN])
    data[WIN_PRICE] = data[PRICE_COLUMN] * (1 + win_percentage / 100)
    data[DRAW_DOWN_PRICE] = data[PRICE_COLUMN] * (1 - draw_down_percentage / 100)

    data[MIN_VALUE_COLUMN], data[MIN_INDEX_COLUMN], data[MAX_VALUE_COLUMN], data[
        MAX_INDEX_COLUMN] = get_min_max_with_indices_grouped(data, max_trading_time, TOKEN_COlUMN)

    data = data.dropna()

    data[LABEL_COLUMN] = ((data[WIN_PRICE] <= data[MAX_VALUE_COLUMN]) & (
            data[DRAW_DOWN_PRICE] < data[MIN_VALUE_COLUMN])) | \
                         ((data[WIN_PRICE] <= data[MAX_VALUE_COLUMN]) & (
                                 data[MAX_INDEX_COLUMN] < data[MIN_INDEX_COLUMN]))

    data.drop(
        columns=[WIN_PRICE, DRAW_DOWN_PRICE, MIN_VALUE_COLUMN, MIN_INDEX_COLUMN, MAX_VALUE_COLUMN, MAX_INDEX_COLUMN],
        inplace=True)
    return data


def label_window(full_token_data: pd.DataFrame, window_data: pd.DataFrame,
                 win_percentage: int, draw_down_percentage: int) -> bool:
    last_price = window_data.iloc[-1][PRICE_COLUMN]
    last_minute = window_data.iloc[-1][TRADING_MINUTE_COLUMN]

    win_price = last_price * (1 + win_percentage / 100)
    lost_price = last_price * (1 - draw_down_percentage / 100)

    # Filter rows where the minute is greater than the last minute
    future_data = full_token_data[full_token_data[TRADING_MINUTE_COLUMN] > last_minute]
    future_data[PRICE_COLUMN] = pd.to_numeric(future_data[PRICE_COLUMN], errors='coerce')

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


def label_data_vectorized(full_data: pd.DataFrame, split_data: List[pd.DataFrame],
                          win_percentage: int, draw_down_percentage: int) -> List[pd.DataFrame]:
    # Concatenate split data for bulk operations
    split_data_df = pd.concat(split_data, keys=range(len(split_data)))

    # Calculate win/loss thresholds based on the last price in each window
    last_price = split_data_df.groupby(level=0)[PRICE_COLUMN].transform('last')
    win_price = last_price * (1 + win_percentage / 100)
    draw_down_price = last_price * (1 - draw_down_percentage / 100)

    # Merge split data with full data on token and trading minute to access future prices
    merged_data = split_data_df.reset_index().merge(
        full_data, on=[TOKEN_COlUMN, TRADING_MINUTE_COLUMN], suffixes=('', '_full')
    )

    # Compare future prices with win and drawdown thresholds
    merged_data['win_met'] = merged_data[PRICE_COLUMN + '_full'] >= win_price
    merged_data['drawdown_met'] = merged_data[PRICE_COLUMN + '_full'] <= draw_down_price

    # Get first instances of win and drawdown in future data
    win_met_index = merged_data.groupby('level_0')['win_met'].idxmax()
    drawdown_met_index = merged_data.groupby('level_0')['drawdown_met'].idxmax()

    # Determine label based on which condition is met first
    merged_data[LABEL_COLUMN] = np.where(
        (win_met_index < drawdown_met_index) & win_met_index.notna(),
        True,
        False
    )

    # Add labels back to split_data DataFrames
    labeled_split_data = []
    for key, df in split_data_df.groupby(level=0):
        df[LABEL_COLUMN] = merged_data.loc[merged_data['level_0'] == key, LABEL_COLUMN].values
        labeled_split_data.append(df.droplevel(0))

    # Logging
    amount_of_true = merged_data[LABEL_COLUMN].sum()
    amount_of_false = len(merged_data) - amount_of_true
    logger.info("Amount of true windows: %s, Amount of false windows: %s", amount_of_true, amount_of_false)

    return labeled_split_data

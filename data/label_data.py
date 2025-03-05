import pandas as pd

from constants import PRICE_COLUMN, TRADING_MINUTE_COLUMN, LABEL_COLUMN, TOKEN_COLUMN

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
        MIN_VALUE_COLUMN: min_value,
        MIN_INDEX_COLUMN: min_index,
        MAX_VALUE_COLUMN: max_value,
        MAX_INDEX_COLUMN: max_index
    })


def label_dataset(data: pd.DataFrame, win_percentage: int,
                  draw_down_percentage: int, max_trading_time: int) -> pd.DataFrame:
    # Sort by token and trading minute
    data = data.sort_values(by=[TOKEN_COLUMN, TRADING_MINUTE_COLUMN])
    data[WIN_PRICE] = data[PRICE_COLUMN] * (1 + win_percentage / 100)
    draw_down_percentage = draw_down_percentage if draw_down_percentage != "infinite" else 9999
    data[DRAW_DOWN_PRICE] = data[PRICE_COLUMN] * (1 - draw_down_percentage / 100)

    data[MIN_VALUE_COLUMN], data[MIN_INDEX_COLUMN], data[MAX_VALUE_COLUMN], data[
        MAX_INDEX_COLUMN] = get_min_max_with_indices_grouped(data, max_trading_time, TOKEN_COLUMN)

    data = data.dropna()
    if draw_down_percentage == 9999:
        data[LABEL_COLUMN] = data[WIN_PRICE] <= data[MAX_VALUE_COLUMN]
    else:
        data[LABEL_COLUMN] = ((data[WIN_PRICE] <= data[MAX_VALUE_COLUMN]) & (
                data[DRAW_DOWN_PRICE] < data[MIN_VALUE_COLUMN])) | \
                             ((data[WIN_PRICE] <= data[MAX_VALUE_COLUMN]) & (
                                     data[MAX_INDEX_COLUMN] < data[MIN_INDEX_COLUMN]))

    data.drop(
        columns=[WIN_PRICE, DRAW_DOWN_PRICE, MIN_VALUE_COLUMN, MIN_INDEX_COLUMN, MAX_VALUE_COLUMN, MAX_INDEX_COLUMN],
        inplace=True)
    return data


def label_without_time_window(data: pd.DataFrame, win_percentage: int) -> pd.DataFrame:
    data[LABEL_COLUMN] = data[(data[TOKEN_COLUMN] == data[TOKEN_COLUMN]) &
                              (data[TRADING_MINUTE_COLUMN] > data[TRADING_MINUTE_COLUMN]) & (
                                          data[PRICE_COLUMN] * (1 + win_percentage / 100) <= data[PRICE_COLUMN])]
    return data
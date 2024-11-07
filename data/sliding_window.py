from typing import List

import pandas as pd

from constants import TOKEN_COlUMN, TRADING_MINUTE_COLUMN


def unroll_data(data: List[pd.DataFrame]) -> pd.DataFrame:
    """
    Concatenates a list of DataFrames into a single DataFrame.

    Parameters:
    - data (List[pd.DataFrame]): List of DataFrames to concatenate.

    Returns:
    - pd.DataFrame: A single DataFrame containing all rows from the input DataFrames.
    """
    return pd.concat(data, ignore_index=True)


def contains_non_zero_trade_state(df: pd.DataFrame) -> bool:
    """
    Check if any of the columns with names matching 'trade_(wallet_address)_state'
    contain a value other than 0.

    Args:
        df (pd.DataFrame): The DataFrame to check.

    Returns:
        bool: True if any non-zero value is found in the specified columns, False otherwise.
    """
    trade_columns = df.filter(regex=r'^trader_.*_state$')
    return (trade_columns != 0).any().any()


def create_sliding_windows(data: pd.DataFrame, window_size: int = 10, step_size: int = 1) -> List[pd.DataFrame]:
    """
    Splits data into sliding windows for each token.

    Parameters:
    data (pd.DataFrame): DataFrame with 'trading_minute', 'token', and other features.
    window_size (int): The size of each window in minutes.
    step_size (int): The step size for sliding the window in minutes.

    Returns:
    List[pd.DataFrame]: A list of DataFrames, each representing a sliding window of the data.
    """
    sliding_windows = []

    # Process each token individually
    for token in data[TOKEN_COlUMN].unique():
        # Filter data for this token
        token_data = data[data[TOKEN_COlUMN] == token].sort_values(TRADING_MINUTE_COLUMN).reset_index(drop=True)

        # Create sliding windows
        for start in range(0, len(token_data) - window_size + 1, step_size):
            end = start + window_size
            window = token_data.iloc[start:end]

            # Only add the window if it has the full desired size (to avoid partial windows at the end)
            if len(window) == window_size and contains_non_zero_trade_state(window):
                sliding_windows.append(window)

    return sliding_windows

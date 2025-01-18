from typing import List

import pandas as pd

from constants import TOKEN_COlUMN, TRADING_MINUTE_COLUMN


def get_sizes_from_data(data: List[pd.DataFrame]) -> List[int]:
    """
    Returns the size of each original DataFrame in the list, assuming all DataFrames are the same size.

    Parameters:
    - data (List[pd.DataFrame]): The list of original DataFrames.

    Returns:
    - List[int]: A list of row counts for each original DataFrame.
    """
    # Assuming all DataFrames have the same number of rows, we take the size of the first DataFrame
    num_rows = len(data[0])  # Number of rows in each DataFrame
    sizes = [num_rows] * len(data)  # All DataFrames have the same size

    return sizes


def roll_back_data(df: pd.DataFrame, sizes: List[int]) -> List[pd.DataFrame]:
    """
    Reverses the unrolling of data by splitting a single DataFrame into a list of DataFrames.

    Parameters:
    - df (pd.DataFrame): The concatenated DataFrame to split.
    - sizes (List[int]): List of row counts representing the size of each original DataFrame.

    Returns:
    - List[pd.DataFrame]: A list of DataFrames split according to the provided sizes.
    """
    # Initialize a list to hold the resulting DataFrames
    dfs = []

    # Split the DataFrame into chunks based on the sizes
    start_idx = 0
    for size in sizes:
        end_idx = start_idx + size
        dfs.append(df.iloc[start_idx:end_idx].reset_index(drop=True))
        start_idx = end_idx

    return dfs


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


def create_sliding_window_flat(data: pd.DataFrame, step_size: int = 1):
    if step_size <= 0:
        raise ValueError('step_size must be greater than 0')

    return data.groupby(TOKEN_COlUMN).apply(lambda df: df.iloc[::step_size]).reset_index(drop=True)


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

        # Add padding rows with 0 values
        padding = pd.DataFrame(
            {col: [None] * (window_size - 1) for col in token_data.columns}
        )
        token_data = pd.concat([padding, token_data], ignore_index=True)

        # Create sliding windows
        for start in range(0, len(token_data) - window_size + 1, step_size):
            end = start + window_size
            window = token_data.iloc[start:end].copy()

            window = window.dropna()

            # Only add the window if it has the full desired size (to avoid partial windows at the end)
            if contains_non_zero_trade_state(window):
                sliding_windows.append(window)

    return sliding_windows

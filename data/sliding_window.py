
import pandas as pd
from typing import List

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
    for token in data['token'].unique():
        # Filter data for this token
        token_data = data[data['token'] == token].sort_values('trading_minute').reset_index(drop=True)

        # Create sliding windows
        for start in range(0, len(token_data) - window_size + 1, step_size):
            end = start + window_size
            window = token_data.iloc[start:end]

            # Only add the window if it has the full desired size (to avoid partial windows at the end)
            if len(window) == window_size:
                sliding_windows.append(window)

    return sliding_windows
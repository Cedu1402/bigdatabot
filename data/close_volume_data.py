import pandas as pd


def add_missing_minutes(data: pd.DataFrame) -> pd.DataFrame:
    """
    Add missing minutes to trading data for each token over a 4-hour period.

    Parameters:
    data (pd.DataFrame): DataFrame with 'trading_minute' and 'token' columns

    Returns:
    pd.DataFrame: DataFrame with filled missing minutes
    """
    # Convert trading_minute to datetime if not already
    data['trading_minute'] = pd.to_datetime(data['trading_minute'])

    filled_dfs = []
    for token in data['token'].unique():
        # Filter for the specific token
        token_df = data[data['token'] == token].set_index('trading_minute')

        # Define the 4-hour range for this token
        min_time = token_df.index.min()
        max_time = min_time + pd.Timedelta(hours=4) - pd.Timedelta(minutes=1)
        full_range = pd.date_range(start=min_time, end=max_time, freq='min')

        # Reindex with the 4-hour minute range and forward fill
        # Add explicit dtype preservation to avoid downcasting warning
        token_filled = token_df.reindex(full_range)
        token_filled = token_filled.infer_objects()
        token_filled = token_filled.ffill()

        # Reset index and add the token column back
        token_filled = token_filled.reset_index().rename(columns={'index': 'trading_minute'})
        token_filled['token'] = token

        filled_dfs.append(token_filled)

    # Concatenate all token dataframes and sort
    filled_df = pd.concat(filled_dfs, ignore_index=True)
    filled_df = filled_df.sort_values(by=['token', 'trading_minute']).reset_index(drop=True)

    return filled_df
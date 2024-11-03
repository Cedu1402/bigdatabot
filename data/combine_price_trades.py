import pandas as pd


def add_trader_info_to_price_data(price_data: pd.DataFrame,
                                  trader: pd.DataFrame,
                                  trades: pd.DataFrame) -> pd.DataFrame:
    """
    Add trader-specific buy/sell volumes to price data for each trading minute and token.

    Parameters:
    price_data (pd.DataFrame): DataFrame with trading_minute, token, buy_volume, sell_volume, latest_price
    trader (pd.DataFrame): DataFrame with trader IDs
    trades (pd.DataFrame): DataFrame with individual trades (trader_id, token, block_time, buy, token_sold_amount/token_bought_amount)

    Returns:
    pd.DataFrame: Original price data with additional columns for each trader's buy/sell volumes
    """
    # Ensure datetime format
    price_data['trading_minute'] = pd.to_datetime(price_data['trading_minute'])
    trades['block_time'] = pd.to_datetime(trades['block_time'])

    # Create trading_minute column in trades data
    trades['trading_minute'] = trades['block_time'].dt.floor('min')

    # Initialize result DataFrame
    result = price_data.copy()

    # Process each trader
    for trader_id in trader['trader'].unique():
        # Filter trades for this trader
        trader_trades = trades[trades['trader_id'] == trader_id]

        # Calculate buy volumes per minute and token
        buy_trades = trader_trades[trader_trades['buy'] == 1].groupby(['trading_minute', 'token'])[
            'token_sold_amount'].sum().reset_index()
        buy_trades = buy_trades.rename(columns={'token_sold_amount': f'trader_{trader_id}_buy'})

        # Calculate sell volumes per minute and token
        sell_trades = trader_trades[trader_trades['buy'] == 0].groupby(['trading_minute', 'token'])[
            'token_bought_amount'].sum().reset_index()
        sell_trades = sell_trades.rename(columns={'token_bought_amount': f'trader_{trader_id}_sell'})

        # Merge buy volumes
        result = pd.merge(result, buy_trades, on=['trading_minute', 'token'], how='left')
        result[f'trader_{trader_id}_buy'] = result[f'trader_{trader_id}_buy'].fillna(0)

        # Merge sell volumes
        result = pd.merge(result, sell_trades, on=['trading_minute', 'token'], how='left')
        result[f'trader_{trader_id}_sell'] = result[f'trader_{trader_id}_sell'].fillna(0)

    return result.sort_values(['token', 'trading_minute'])

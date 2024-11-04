import math
from dataclasses import dataclass
from typing import Tuple, Union, NoReturn

import pandas as pd


@dataclass
class TraderState:
    NO_ACTION = 0  # neither bought nor sold
    JUST_BOUGHT = 1  # bought in current minute
    STILL_HOLDS = 2  # held from previous minute
    JUST_SOLD = 3  # sold in current minute
    NUKED = 4  # sold all in one clip
    SOLD_ALL = 5  # sold all in one clip


class TraderStateError(Exception):
    """Base exception for trader state determination errors."""
    pass


class InvalidPositionError(TraderStateError):
    """Exception raised for invalid position values (NaN, Inf)."""

    def __init__(self, position_name: str, value):
        self.position_name = position_name
        self.value = value
        super().__init__(f"Invalid {position_name}: {value}")


def prepare_timestamps(price_data: pd.DataFrame, trades: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Prepare and standardize timestamp formats."""
    price_data = price_data.copy()
    trades = trades.copy()

    price_data['trading_minute'] = pd.to_datetime(price_data['trading_minute'])
    trades['block_time'] = pd.to_datetime(trades['block_time'])
    trades['trading_minute'] = trades['block_time'].dt.floor('min')

    return price_data, trades


def calculate_minute_positions(trader_trades: pd.DataFrame) -> pd.DataFrame:
    """Calculate net positions for each minute and token for a trader."""
    if len(trader_trades) == 0:
        return pd.DataFrame(columns=['trading_minute', 'token', 'net_position'])

    positions = []
    for (minute, token), group in trader_trades.groupby(['trading_minute', 'token']):
        buys = group[group['buy'] == 1]['token_sold_amount'].sum()
        sells = group[group['buy'] == 0]['token_bought_amount'].sum()
        positions.append({
            'trading_minute': minute,
            'token': token,
            'net_position': buys - sells
        })

    return pd.DataFrame(positions)


def validate_position(position: float, name: str):
    """
    Validate a position value is a valid finite number.

    Args:
        position: The position value to validate
        name: Name of the position for error messaging

    Raises:
        InvalidPositionError: If position is NaN or Infinite
    """
    if not isinstance(position, (int, float)):
        raise InvalidPositionError(name, position)
    if math.isnan(position):
        raise InvalidPositionError(name, "NaN")
    if math.isinf(position):
        raise InvalidPositionError(name, "Infinite")


def determine_trader_state(
        net_position: float,
        cumulative_position: float,
        previous_position: float
) -> int:
    """Determine the trader's state based on their positions."""

    validate_position(net_position, "net_position")
    validate_position(cumulative_position, "cumulative_position")
    validate_position(previous_position, "previous_position")

    if net_position > 0:
        return TraderState.JUST_BOUGHT
    elif net_position < 0:
        if abs(net_position) >= previous_position:
            return TraderState.NUKED
        return TraderState.JUST_SOLD
    elif cumulative_position > 0:
        return TraderState.STILL_HOLDS
    return TraderState.NO_ACTION


def update_trader_states(
        result: pd.DataFrame,
        token: str,
        trader_id: str,
        positions_df: pd.DataFrame,
        cumulative_positions: pd.Series
) -> pd.DataFrame:
    """Update trader states for a specific token."""
    token_mask = (result['token'] == token)

    for idx, row in positions_df[positions_df['token'] == token].sort_values('trading_minute').iterrows():
        minute_mask = (result['trading_minute'] == row['trading_minute']) & token_mask
        position_before = cumulative_positions.loc[:idx].shift(1).fillna(0).iloc[-1]
        current_position = cumulative_positions.loc[:idx].sum()

        state = determine_trader_state(
            row['net_position'],
            current_position,
            position_before
        )

        result.loc[minute_mask, f'trader_{trader_id}_state'] = state
        holding_mask = (
                (result['trading_minute'] > row['trading_minute']) &
                token_mask
        )
        if state == TraderState.JUST_BOUGHT or state == TraderState.JUST_SOLD:
            result.loc[holding_mask, f'trader_{trader_id}_state'] = TraderState.STILL_HOLDS
        elif state == TraderState.NUKED:
            result.loc[holding_mask, f'trader_{trader_id}_state'] = TraderState.SOLD_ALL

    return result


def add_trader_info_to_price_data(
        price_data: pd.DataFrame,
        trader: pd.DataFrame,
        trades: pd.DataFrame
) -> pd.DataFrame:
    """
    Add trader specific information to 1m price data.

    Parameters:
    price_data (pd.DataFrame): DataFrame with trading_minute, token, buy_volume, sell_volume, latest_price
    trader (pd.DataFrame): DataFrame with trader IDs
    trades (pd.DataFrame): DataFrame with individual trades (trader_id, token, block_time, buy, token_sold_amount/token_bought_amount)

    Returns:
    pd.DataFrame: Original price data with additional columns for each trader's state
    """
    # Prepare data
    result, trades = prepare_timestamps(price_data, trades)

    # Process each trader
    for trader_id in trader['trader'].unique():
        # Initialize trader state column
        result[f'trader_{trader_id}_state'] = TraderState.NO_ACTION

        # Get trader's trades and positions
        trader_trades = trades[trades['trader_id'] == trader_id]
        positions_df = calculate_minute_positions(trader_trades)

        if positions_df.empty:
            continue

        # Process each token
        for token in positions_df['token'].unique():
            token_positions = positions_df[positions_df['token'] == token].sort_values('trading_minute')
            cumulative_positions = token_positions['net_position'].cumsum()

            result = update_trader_states(
                result,
                token,
                trader_id,
                positions_df,
                cumulative_positions
            )

    return result.sort_values(['token', 'trading_minute'])

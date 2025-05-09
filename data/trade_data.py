from collections import defaultdict
from datetime import datetime, timedelta
from typing import List, Dict

import pandas as pd

from constants import TRADING_MINUTE_COLUMN
from data.combine_price_trades import TraderState
from dto.trade_model import Trade


def group_trades_by_trader(trades: List[Trade]) -> Dict[str, List[Trade]]:
    traders = defaultdict(list)
    for trade in trades:
        traders[trade.trader].append(trade)
    return traders


def get_traders(trades: List[Trade]) -> List[str]:
    traders = set()
    for trade in trades:
        traders.add(trade.trader)
    return list(traders)


def get_valid_trades(trades: List[Trade], trading_minute: datetime) -> List[Trade]:
    return [trade for trade in trades if
            trade.get_time() <= trading_minute + timedelta(minutes=1) - timedelta(microseconds=1)]


def get_end_of_current_minute(minute: datetime) -> datetime:
    return minute + timedelta(minutes=1) - timedelta(microseconds=1)


def get_trade_state(last_trade: Trade) -> TraderState:
    if last_trade.buy:
        return TraderState.JUST_BOUGHT
    elif not last_trade.buy:
        if last_trade.token_holding_after > 1:
            return TraderState.JUST_SOLD
        else:
            return TraderState.NUKED


def get_trade_state_no_trade_in_minute(last_trade_state: TraderState, last_trade: Trade) -> TraderState:
    if ((last_trade_state is TraderState.NO_ACTION and last_trade.buy)
            or last_trade_state == TraderState.JUST_BOUGHT
            or last_trade_state == TraderState.JUST_SOLD):
        return TraderState.STILL_HOLDS
    elif last_trade_state == TraderState.NUKED:
        return TraderState.SOLD_ALL
    else:
        return TraderState.NO_ACTION


def get_previous_trades_by_trader(trades: List[Trade], trading_minute: datetime) -> Dict[str, List[Trade]]:
    trader_trades = dict()
    for trade in trades:

        if trade.get_time().replace(second=0, microsecond=0) > trading_minute:
            continue

        if trade.trader not in trader_trades:
            trader_trades[trade.trader] = list()

        trader_trades[trade.trader].append(trade)

    return trader_trades


def create_dataframe_with_trades(trades: List[Trade], trading_minute: datetime, time_frame: int) -> pd.DataFrame:
    data = list(dict())
    all_traders = [trade.trader for trade in trades]

    for i in range(time_frame):
        current_trading_minute = trading_minute - timedelta(minutes=i)
        current_data = {TRADING_MINUTE_COLUMN: current_trading_minute}
        trader_dict = get_previous_trades_by_trader(trades, current_trading_minute)

        for trader in all_traders:
            trader_trades = trader_dict.get(trader, [])
            current_data[f"{trader}_sol_amount_spent"] = sum([item.sol_amount for item in trader_trades if item.buy])
            current_data[f"{trader}_sol_amount_received"] = sum(
                [item.sol_amount for item in trader_trades if not item.buy])

        data.append(current_data)

    return pd.DataFrame(data)


def add_trader_actions_to_dataframe(trades: List[Trade], trading_minute: datetime) -> pd.DataFrame:
    traders = group_trades_by_trader(trades)
    df = pd.DataFrame()

    for key, value in traders.items():
        data = list()
        last_trade_state = TraderState.NO_ACTION

        for i in range(10):
            current_minute = trading_minute - timedelta(minutes=9 - i)
            end_current_minute = get_end_of_current_minute(current_minute)
            current_trades = [trade for trade in value if trade.get_time() <= end_current_minute]
            last_trade = max(current_trades, key=lambda trade: trade.get_time(), default=None)
            if last_trade is None:
                data.append(TraderState.NO_ACTION)
                continue

            if last_trade.get_time() >= current_minute:
                last_trade_state = get_trade_state(last_trade)
                data.append(last_trade_state)
            else:
                data.append(get_trade_state_no_trade_in_minute(last_trade_state, last_trade))

        df["trader_" + key + "_state"] = data

    return df

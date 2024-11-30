from collections import defaultdict
from datetime import datetime, timedelta
from typing import List, Dict

import pandas as pd

from data.combine_price_trades import TraderState
from solana_api.trade_model import Trade


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
            trade.time <= trading_minute + timedelta(minutes=1) - timedelta(microseconds=1)]


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


def add_trader_actions_to_dataframe(trades: List[Trade], trading_minute: datetime) -> pd.DataFrame:
    traders = group_trades_by_trader(trades)
    df = pd.DataFrame()

    for key, value in traders.items():
        data = list()
        last_trade_state = TraderState.NO_ACTION

        for i in range(10):
            current_minute = trading_minute - timedelta(minutes=9 - i)
            end_current_minute = get_end_of_current_minute(current_minute)
            current_trades = [trade for trade in value if trade.time <= end_current_minute]
            last_trade = max(current_trades, key=lambda trade: trade.time, default=None)
            if last_trade is None:
                data.append(TraderState.NO_ACTION)
                continue

            if last_trade.time >= current_minute:
                last_trade_state = get_trade_state(last_trade)
                data.append(last_trade_state)
            else:
                data.append(get_trade_state_no_trade_in_minute(last_trade_state, last_trade))

        df["trader_" + key + "_state"] = data

    return df

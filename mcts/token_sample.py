import asyncio
import random
from datetime import datetime
from typing import List, Dict

import numpy as np
import pandas as pd

from constants import TOKEN_COlUMN, TRADING_MINUTE_COLUMN, PRICE_COLUMN
from data.combine_price_trades import prepare_timestamps
from dune.data_collection import collect_all_data


def filter_out_pre_trade_data(price_data: pd.DataFrame, trades: pd.DataFrame) -> pd.DataFrame:
    price_data, trades = prepare_timestamps(price_data, trades)
    first_trade_per_token = trades.groupby(TOKEN_COlUMN)[TRADING_MINUTE_COLUMN].min()

    # Map each row to its corresponding first trade time
    price_data['first_trade_time'] = price_data[TOKEN_COlUMN].map(first_trade_per_token)

    # Filter where trading minute is after or equal to the first trade
    filtered = price_data[price_data[TRADING_MINUTE_COLUMN] >= price_data['first_trade_time']]

    return filtered.drop(columns=['first_trade_time']).reset_index(drop=True)


def load_token_ohlcv_data() -> pd.DataFrame:
    price_data, trades = asyncio.run(collect_all_data(True))
    price_data = filter_out_pre_trade_data(price_data, trades)
    return price_data


def remove_current_token(token_ohlcv_data: pd.DataFrame, token: str) -> pd.DataFrame:
    return token_ohlcv_data[token_ohlcv_data[TOKEN_COlUMN] != token].reset_index(drop=True)


def remove_older_tokens(token_ohlcv_data: pd.DataFrame, start_date: datetime) -> pd.DataFrame:
    return (
        token_ohlcv_data
        .groupby(TOKEN_COlUMN)
        .filter(lambda df: df[TRADING_MINUTE_COLUMN].min() >= start_date)
        .reset_index(drop=True)
    )


def get_token_list(token_ohlcv_data: pd.DataFrame) -> List[str]:
    return list(token_ohlcv_data[TOKEN_COlUMN].unique())


def sample_tokens(token_list: List[str], amount: int) -> List[str]:
    return random.sample(token_list, amount)


def get_filtered_data(token_ohlcv_data: pd.DataFrame, selected_tokens: List[str]) -> pd.DataFrame:
    return token_ohlcv_data[token_ohlcv_data[TOKEN_COlUMN].isin(selected_tokens)].reset_index(drop=True)


def split_by_token(token_ohlcv_data: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    return {str(token): df.reset_index(drop=True) for token, df in token_ohlcv_data.groupby(TOKEN_COlUMN)}


def add_price_pct_column(token_ohlcv_data: pd.DataFrame) -> pd.DataFrame:
    return token_ohlcv_data.groupby(TOKEN_COlUMN, group_keys=False).apply(
        lambda df: df.assign(
            price_pct_change=df[PRICE_COLUMN].replace(0, np.nan).pct_change().fillna(0.0).astype('float64'))
    )


def get_info_sets(data: pd.DataFrame) -> List[List[float]]:
    return [
        df[PRICE_COLUMN].pct_change().dropna().tolist()
        for _, df in data.groupby(TOKEN_COlUMN)
    ]


def sample_random_tokens(token: str, token_ohlcv_data: pd.DataFrame, amount: int,
                         token_start_date: datetime) -> pd.DataFrame:
    """
    :param token: token we run mcts on
    :param token_ohlcv_data: ohlcv data of tokens
    :param amount: amount of tokens to sample
    :param token_start_date: start date of token
    :return: tokens ohlcv data
    """
    # todo only from current token age on. (add token age param and filter data for each token sampled).
    token_ohlcv_data = remove_current_token(token_ohlcv_data, token)
    token_ohlcv_data = remove_older_tokens(token_ohlcv_data, token_start_date)
    selected_tokens = sample_tokens(get_token_list(token_ohlcv_data), amount)

    return get_filtered_data(token_ohlcv_data, selected_tokens)

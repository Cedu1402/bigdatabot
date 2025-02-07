import asyncio
import random
from datetime import datetime
from typing import List, Dict, Tuple

import numpy as np
import pandas as pd

from cache_helper import write_data_to_cache
from constants import TOKEN_COlUMN, TRADING_MINUTE_COLUMN, PRICE_COLUMN, LAUNCH_DATE_COLUMN, PRICE_PCT_CHANGE, \
    CURRENT_ASSET_PRICE_COLUMN
from data.cache_data import read_cache_data
from data.combine_price_trades import prepare_timestamps
from data.feature_engineering import add_launch_date
from dune.data_collection import collect_all_data


def load_token_ohlcv_data() -> Tuple[pd.DataFrame, pd.DataFrame]:
    file_name = 'load_token_ohlcv_data'

    cached_data = read_cache_data(file_name)
    if cached_data is not None:
        return cached_data[0], cached_data[1]

    price_data, trades = asyncio.run(collect_all_data(True))
    price_data, trades = prepare_timestamps(price_data, trades)
    price_data = add_launch_date(trades, price_data)
    price_data = add_token_age_column(price_data)
    price_data = add_price_pct_column(price_data)
    write_data_to_cache(file_name, (price_data, trades))

    return price_data, trades


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
    return random.sample(token_list, amount if len(token_list) > amount else len(token_list))


def get_filtered_data(token_ohlcv_data: pd.DataFrame, selected_tokens: List[str]) -> pd.DataFrame:
    return token_ohlcv_data[token_ohlcv_data[TOKEN_COlUMN].isin(selected_tokens)].reset_index(drop=True)


def split_by_token(token_ohlcv_data: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    return {str(token): df.reset_index(drop=True) for token, df in token_ohlcv_data.groupby(TOKEN_COlUMN)}


def add_token_age_column(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby(TOKEN_COlUMN, group_keys=False).apply(
        lambda group: group.assign(
            age_in_minutes=np.ceil((group[TRADING_MINUTE_COLUMN] - group[LAUNCH_DATE_COLUMN]).dt.total_seconds() / 60)
        )
    )


def add_price_pct_column(token_ohlcv_data: pd.DataFrame) -> pd.DataFrame:
    return token_ohlcv_data.groupby(TOKEN_COlUMN, group_keys=False).apply(
        lambda df: df.assign(
            price_pct_change=df[PRICE_COLUMN].replace(0, np.nan).pct_change().fillna(0.0).astype('float64'))
    )


def get_info_sets(data: pd.DataFrame) -> List[pd.DataFrame]:
    return [
        df[[PRICE_PCT_CHANGE, CURRENT_ASSET_PRICE_COLUMN]].reset_index(drop=True) for _, df in
        data.groupby(TOKEN_COlUMN)
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

    token_ohlcv_data = remove_current_token(token_ohlcv_data, token)
    token_ohlcv_data = remove_older_tokens(token_ohlcv_data, token_start_date)
    selected_tokens = sample_tokens(get_token_list(token_ohlcv_data), amount)

    return get_filtered_data(token_ohlcv_data, selected_tokens)

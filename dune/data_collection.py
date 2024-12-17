from typing import Tuple

import pandas as pd

from constants import PRODUCTION_TEST_TRADES, PRODUCTION_TEST_PRICE
from dune.dune_queries import get_list_of_trades, get_close_volume_1m, get_current_trade_list_query, \
    get_current_close_volume_1m_query
from dune.query_request import get_query_result_with_params


def collect_test_data(token: str, use_cache: bool) -> Tuple[pd.DataFrame, pd.DataFrame]:
    top_trader_trades = get_query_result_with_params(PRODUCTION_TEST_TRADES,
                                                     {"min_token_age_h": 2,
                                                      "token": token},
                                                     use_cache)

    volume_close_1m = get_query_result_with_params(PRODUCTION_TEST_PRICE,
                                                   {"min_token_age_h": 2,
                                                    "token": token},
                                                   use_cache)

    return volume_close_1m, top_trader_trades


def collect_all_data(use_cache: bool) -> Tuple[pd.DataFrame, pd.DataFrame]:
    top_trader_trades = get_list_of_trades(use_cache)

    tokens = top_trader_trades['token'].unique().tolist()

    volume_close_1m = get_close_volume_1m(use_cache)

    return volume_close_1m, top_trader_trades


def collect_validation_data(use_cache: bool) -> Tuple[pd.DataFrame, pd.DataFrame]:
    top_trader_trades = get_current_trade_list_query(use_cache)

    volume_close_1m = get_current_close_volume_1m_query(use_cache)

    return volume_close_1m, top_trader_trades


if __name__ == '__main__':
    use_cached_data = True
    collect_all_data(use_cached_data)

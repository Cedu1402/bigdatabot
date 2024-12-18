from datetime import timedelta, datetime
from typing import Tuple, List, Optional, Union, Dict

import pandas as pd

from birdeye_api.ohlcv_endpoint import get_ohlcv, ohlcv_to_dataframe
from cache_helper import cache_exists, get_cache_data, write_data_to_cache
from constants import PRODUCTION_TEST_TRADES, PRODUCTION_TEST_PRICE, TOKEN_CLOSE_VOLUME_1M_QUERY, \
    CURRENT_CLOSE_VOLUME_1M_QUERY
from dune.dune_queries import get_list_of_trades, get_current_trade_list_query, \
    get_current_close_volume_1m_query
from dune.query_request import get_query_result_with_params


async def collect_test_data(token: str, use_cache: bool) -> Tuple[pd.DataFrame, pd.DataFrame]:
    top_trader_trades = get_query_result_with_params(PRODUCTION_TEST_TRADES,
                                                     {"min_token_age_h": 2,
                                                      "token": token},
                                                     use_cache)

    volume_close_1m = get_query_result_with_params(PRODUCTION_TEST_PRICE,
                                                   {"min_token_age_h": 2,
                                                    "token": token},
                                                   use_cache)

    return volume_close_1m, top_trader_trades


def get_cache_file_data(query_id: Union[int, str]) -> Optional[pd.DataFrame]:
    if cache_exists(str(query_id)):
        return get_cache_data(str(query_id))
    return None


async def load_volume_1m_data_form_brideye(tokens: List[str], launch_times: Dict[str, datetime]) -> pd.DataFrame:
    all_volume_data = []
    for token in tokens:
        end_time = launch_times[token] + timedelta(hours=4)
        ohlcv_data = await get_ohlcv(token, launch_times[token], end_time, "1m", check_counter=False)
        volume_data = ohlcv_to_dataframe(ohlcv_data)
        all_volume_data.append(volume_data)

    volume_close_1m = pd.concat(all_volume_data, ignore_index=True)
    return volume_close_1m


async def get_close_volume_1m(tokens: List[str], launch_times: Dict[str, datetime], use_cache: bool, query_name: str) -> pd.DataFrame:
    if use_cache:
        result_data = get_cache_file_data(query_name)
        if result_data is not None:
            return result_data  # Return cached data if available

    result = await load_volume_1m_data_form_brideye(tokens, launch_times)
    write_data_to_cache(query_name, result)
    return result


def get_tokens_and_launch_dict(top_trader_trades: pd.DataFrame) -> Tuple[List[str], Dict[str, datetime]]:
    top_trader_trades['launch_time'] = pd.to_datetime(top_trader_trades['launch_time'])
    tokens = top_trader_trades['token'].unique().tolist()
    launch_times = dict(zip(top_trader_trades['token'], top_trader_trades['launch_time']))
    return tokens, launch_times


async def collect_all_data(use_cache: bool) -> Tuple[pd.DataFrame, pd.DataFrame]:
    top_trader_trades = get_list_of_trades(use_cache)
    tokens, launch_times = get_tokens_and_launch_dict(top_trader_trades)
    volume_close_1m = await get_close_volume_1m(tokens, launch_times, use_cache, TOKEN_CLOSE_VOLUME_1M_QUERY)

    return volume_close_1m, top_trader_trades


async def collect_validation_data(use_cache: bool) -> Tuple[pd.DataFrame, pd.DataFrame]:
    top_trader_trades = get_current_trade_list_query(use_cache)

    tokens, launch_times = get_tokens_and_launch_dict(top_trader_trades)
    volume_close_1m = await get_close_volume_1m(tokens, launch_times, use_cache, CURRENT_CLOSE_VOLUME_1M_QUERY)

    return volume_close_1m, top_trader_trades


if __name__ == '__main__':
    use_cached_data = True
    collect_all_data(use_cached_data)

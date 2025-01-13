from datetime import timedelta, datetime
from typing import Tuple, List, Dict

import pandas as pd

from birdeye_api.ohlcv_endpoint import get_ohlcv, ohlcv_to_dataframe
from birdeye_api.token_creation_endpoint import get_token_create_info
from birdeye_api.trades_endpoint import get_top_trader_trades_from_birdeye
from cache_helper import write_data_to_cache, get_cache_file_data
from constants import PRODUCTION_TEST_TRADES, PRODUCTION_TEST_PRICE, TOKEN_CLOSE_VOLUME_1M_QUERY, \
    CURRENT_CLOSE_VOLUME_1M_QUERY
from dune.dune_queries import get_current_trade_list_query, get_top_traders
from dune.query_request import get_query_result_with_params


async def collect_test_data(token: str, use_cache: bool) -> Tuple[pd.DataFrame, pd.DataFrame]:
    top_trader_trades = get_query_result_with_params(PRODUCTION_TEST_TRADES,
                                                     {"min_token_age_h": 2,
                                                      "token": token},
                                                     use_cache)
    launch_time, _ = await get_token_create_info(token, api_limit=True)
    volume_close_1m = await get_close_volume_1m([token],
                                                {token: launch_time},
                                                use_cache,
                                                str(PRODUCTION_TEST_PRICE) + token)

    return volume_close_1m, top_trader_trades


async def load_volume_1m_data_form_brideye(tokens: List[str], launch_times: Dict[str, datetime]) -> pd.DataFrame:
    all_volume_data = []
    for token in tokens:
        end_time = launch_times[token] + timedelta(hours=4)
        ohlcv_data = await get_ohlcv(token, launch_times[token], end_time, "1m", api_limit=False)
        volume_data = ohlcv_to_dataframe(ohlcv_data)
        all_volume_data.append(volume_data)

    volume_close_1m = pd.concat(all_volume_data, ignore_index=True)
    return volume_close_1m


async def get_close_volume_1m(tokens: List[str], launch_times: Dict[str, datetime], use_cache: bool,
                              query_name: str) -> pd.DataFrame:
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
    end_date = datetime.utcnow() - timedelta(hours=10)
    start_date = end_date - timedelta(days=76)

    top_traders = get_top_traders(use_cache)

    top_trader_trades = await get_top_trader_trades_from_birdeye(top_traders["trader_id"], start_date, end_date)

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

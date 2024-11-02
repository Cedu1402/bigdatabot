from typing import Tuple

import pandas as pd

from dune.top_trader_queries import get_list_of_traders, get_list_of_traded_tokens, get_list_of_trades, \
    get_close_volume_1m


def collect_all_data(use_cache: bool) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    top_trader = get_list_of_traders(use_cache)
    top_trader_trades = get_list_of_trades(use_cache)
    volume_close_1m = get_close_volume_1m(use_cache)

    return top_trader, top_trader_trades, volume_close_1m



if __name__ == '__main__':
    use_cached_data = True
    collect_all_data(use_cached_data)
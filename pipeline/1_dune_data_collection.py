from typing import Tuple

import pandas as pd

from dune.top_trader_queries import get_list_of_traders, get_list_of_traded_tokens, get_list_of_trades


def collect_all_data() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    top_trader = get_list_of_traders()
    token_list = get_list_of_traded_tokens()
    top_trader_trades = get_list_of_trades()



    return top_trader, top_trader_trades, token_list



if __name__ == '__main__':
    collect_all_data()
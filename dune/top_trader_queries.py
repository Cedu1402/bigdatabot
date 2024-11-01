import pandas as pd

from constants import TRADE_LIST_QUERY, TOP_TRADERS_QUERY, TRADED_TOKENS_QUERY
from dune.query_request import get_query_result


def get_list_of_traders() -> pd.DataFrame:
    return get_query_result(TOP_TRADERS_QUERY)


def get_list_of_trades() -> pd.DataFrame:
    return get_query_result(TRADE_LIST_QUERY)


def get_list_of_traded_tokens() -> pd.DataFrame:
    return get_query_result(TRADED_TOKENS_QUERY)

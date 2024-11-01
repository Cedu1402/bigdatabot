import pandas as pd

from constants import TRADE_LIST_QUERY
from dune.query_request import get_query_result


def get_list_of_traders() -> pd.DataFrame:
    return get_query_result(4217799)


def get_list_of_trades():
    return get_query_result(TRADE_LIST_QUERY)


def get_list_of_traded_tokens():
    return get_query_result(4229122)

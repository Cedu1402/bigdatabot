import pandas as pd

from constants import TRADE_LIST_QUERY, TOP_TRADERS_QUERY, TRADED_TOKENS_QUERY, CURRENT_CLOSE_VOLUME_1M_QUERY, \
    CURRENT_TRADE_LIST_QUERY, TOKEN_SAMPLE, MONTHLY_TRADERS_FIRST_BUY
from dune.query_request import get_query_result


def get_list_of_traders(use_cache: bool) -> pd.DataFrame:
    return get_query_result(TOP_TRADERS_QUERY, use_cache)


def get_list_of_trades(use_cache: bool) -> pd.DataFrame:
    return get_query_result(TRADE_LIST_QUERY, use_cache)


def get_top_traders(use_cache: bool) -> pd.DataFrame:
    top_traders = get_query_result(MONTHLY_TRADERS_FIRST_BUY, use_cache)
    return top_traders


def get_token_sample(use_cache: bool) -> pd.DataFrame:
    token_sample = get_query_result(TOKEN_SAMPLE, use_cache)
    return token_sample


def get_list_of_traded_tokens(use_cache: bool) -> pd.DataFrame:
    return get_query_result(TRADED_TOKENS_QUERY, use_cache)


# def get_close_volume_1m(use_cache: bool) -> pd.DataFrame:
#     return get_query_result(TOKEN_CLOSE_VOLUME_1M_QUERY, use_cache)

def get_current_close_volume_1m_query(use_cache: bool) -> pd.DataFrame:
    return get_query_result(CURRENT_CLOSE_VOLUME_1M_QUERY, use_cache)


def get_current_trade_list_query(use_cache: bool) -> pd.DataFrame:
    return get_query_result(CURRENT_TRADE_LIST_QUERY, use_cache)

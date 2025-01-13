import pandas as pd

from constants import TRADE_LIST_QUERY, TOP_TRADERS_QUERY, TRADED_TOKENS_QUERY, CURRENT_CLOSE_VOLUME_1M_QUERY, \
    CURRENT_TRADE_LIST_QUERY, MONTHLY_TRADERS, WEEKLY_TRADERS
from dune.query_request import get_query_result


def get_list_of_traders(use_cache: bool) -> pd.DataFrame:
    return get_query_result(TOP_TRADERS_QUERY, use_cache)


def get_list_of_trades(use_cache: bool) -> pd.DataFrame:
    return get_query_result(TRADE_LIST_QUERY, use_cache)


def get_top_traders(use_cache: bool) -> pd.DataFrame:
    monthly_result = get_query_result(MONTHLY_TRADERS, use_cache)
    weekly_result = get_query_result(WEEKLY_TRADERS, use_cache)
    top_traders = pd.concat([monthly_result, weekly_result], ignore_index=True)
    top_traders = top_traders.drop_duplicates(subset='trader_id', keep='first')
    return top_traders


def get_list_of_traded_tokens(use_cache: bool) -> pd.DataFrame:
    return get_query_result(TRADED_TOKENS_QUERY, use_cache)


# def get_close_volume_1m(use_cache: bool) -> pd.DataFrame:
#     return get_query_result(TOKEN_CLOSE_VOLUME_1M_QUERY, use_cache)

def get_current_close_volume_1m_query(use_cache: bool) -> pd.DataFrame:
    return get_query_result(CURRENT_CLOSE_VOLUME_1M_QUERY, use_cache)


def get_current_trade_list_query(use_cache: bool) -> pd.DataFrame:
    return get_query_result(CURRENT_TRADE_LIST_QUERY, use_cache)

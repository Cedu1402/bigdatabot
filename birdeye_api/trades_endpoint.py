import logging
from datetime import datetime
from typing import List, Dict, Tuple, Optional

import aiohttp
import pandas as pd

from birdeye_api.api_limit import check_api_limit
from blockchain_token.token_creation import check_token_create_info_date_range
from constants import BIRDEYE_KEY
from env_data.get_env_value import get_env_value
from solana_api.jupiter_api import SOL_MINT

logger = logging.getLogger(__name__)


def extract_trade_data(trade: dict) -> Optional[dict]:
    if trade["base"]["address"] != SOL_MINT and trade["quote"]["address"] != SOL_MINT:
        return None

    buy = trade["base"]["address"] == SOL_MINT

    extracted_data = {
        "trader_id": trade["owner"],
        "token_sold_amount": trade["base"]["amount"],
        "token_bought_amount": trade["quote"]["amount"],
        "token": trade["quote"]["address"] if buy else trade["base"]["address"],
        "block_time": datetime.utcfromtimestamp(trade["block_unix_time"]),
        "buy": buy,
        "launch_time": None,
    }

    return extracted_data


async def get_top_trader_trades_from_birdeye(traders: List[str]) -> pd.DataFrame:
    pass


async def get_relevant_tokens(tokens: List[str], start_date: datetime, end_date: datetime) -> List[str]:
    relevant_tokens = []
    for token in tokens:
        result = await check_token_create_info_date_range(token, start_date, end_date)
        if result:
            relevant_tokens.append(token)

    return relevant_tokens


async def get_traded_tokens_of_trader(trader: str, start_date: datetime, end_date: datetime, api_limit: bool = False) -> \
        List[str]:
    trades = await get_trader_trades(trader, start_date, end_date, api_limit)
    tokens = set()

    for trade in trades:
        buy_token = trade['quote']["symbol"]
        sell_token = trade['base']['symbol']

        if buy_token != SOL_MINT:
            tokens.add(buy_token)

        if sell_token != SOL_MINT:
            tokens.add(sell_token)

    return list(tokens)


def validate_response(data: dict, trader: str) -> Tuple[bool, Optional[Dict]]:
    trade_data = data.get("data", None)
    if trade_data is None:
        logger.warning("API response has no data", extra={"trader": trader})
        return False, None

    trades = trade_data.get("items", None)
    if trades is None:
        logger.warning("API response has no trades", extra={"trader": trader})
        return False, None

    return True, trades


async def get_trader_trades(trader: str, start_date: datetime, end_date: datetime, api_limit: bool = False) -> List[
    Dict]:
    """
    Fetches all trades for a specific trader within a given time range from the BirdEye API.

    Args:
        trader (str): The address of the trader.
        start_date (datetime): The start date and time of the requested trade range (UTC).
        end_date (datetime): The end date and time of the requested trade range (UTC).
        api_limit (bool): Checks if BirdEye API limit is reached or not.

    Returns:
        List[Dict]: A list of all trades for the specified trader within the given time frame.

    Raises:
        Exception: If the BirdEye API request limit (50,000) is reached.
        aiohttp.ClientResponseError: If the API response has a non-2xx status code.

    Notes:
        - The BirdEye API provides trade data for traders on the Solana blockchain.
        - This function increments an API call counter in Redis (BIRD_EYE_COUNTER) and logs an error
          if the daily limit is exceeded.
        - Ensure that the Redis counter is initialized and properly configured before using this function.
    """
    url = "https://public-api.birdeye.so/trader/txs/seek_by_time"

    key = get_env_value(BIRDEYE_KEY)
    headers = {
        "accept": "application/json",
        "x-chain": "solana",
        "X-API-KEY": key,
    }

    all_trades = []
    offset = 0
    limit = 100

    while True:
        params = {
            "address": trader,
            "after_time": int(start_date.timestamp()),
            "offset": offset,
            "limit": limit,
            "tx_type": "swap"
        }

        await check_api_limit(api_limit)

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params=params) as response:

                data = await response.json()
                success, trades = validate_response(data, trader)
                if not success:
                    break

                finished = False
                for trade in trades:
                    after_time = trade["block_unix_time"]
                    # Stop if we've passed the end_date
                    if after_time >= int(end_date.timestamp()):
                        finished = True
                        break
                    all_trades.append(trade)

                if data.get("has_next", False) or finished:
                    break

                offset += limit  # Move to the next page

    return all_trades

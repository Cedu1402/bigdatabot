import logging
from datetime import datetime
from typing import List, Dict, Tuple, Optional

import aiohttp
import pandas as pd

from birdeye_api.api_limit import check_api_limit
from blockchain_token.token_creation import check_token_create_info_date_range, get_token_create_info
from cache_helper import get_cache_file_data, write_data_to_cache
from constants import BIRDEYE_KEY, TOP_TRADER_TRADES_BIRDEYE, LAUNCH_DATE_COLUMN, TOKEN_COlUMN
from database.token_creation_info_table import select_token_creation_info_for_list
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


async def get_all_trader_trades(traders: List[str], start_date: datetime, end_date: datetime,
                                api_limit: bool = False):
    trader_trades = list()
    for index, trader in enumerate(traders):
        logger.info(f"Getting trades for {index + 1} of {len(traders)}")
        trades = await get_trader_trades(trader, start_date, end_date, api_limit)
        trader_trades.extend(trades)

    return trader_trades


def get_structured_trade_list(trades: List[dict]) -> List[dict]:
    structured_trader_trades = list()
    for trade in trades:
        trade_data = extract_trade_data(trade)
        structured_trader_trades.append(trade_data)
    return structured_trader_trades


async def get_top_trader_trades_from_birdeye(traders: List[str], start_date: datetime, end_date: datetime,
                                             use_cache: bool = True,
                                             api_limit: bool = False) -> pd.DataFrame:
    logger.info("Starting to fetch top trader trades from Birdeye API")
    if use_cache:
        result_data = get_cache_file_data(TOP_TRADER_TRADES_BIRDEYE)
        if result_data is not None:
            return result_data

    # Step 1: Get trades for all traders
    logger.info("Fetching trades for all traders...")
    trader_trades = None
    cache_key = TOP_TRADER_TRADES_BIRDEYE + "trader_trades"
    if use_cache:
        trader_trades = get_cache_file_data(cache_key)

    if not use_cache or trader_trades is None:
        trader_trades = await get_all_trader_trades(traders, start_date, end_date, api_limit)
        write_data_to_cache(cache_key, trader_trades)

    logger.info(f"Fetched {len(trader_trades)} trades from all traders.")

    # Step 2: Structure the trade data
    logger.info("Structuring trade data...")
    structured_trader_trades = get_structured_trade_list(trader_trades)
    structured_trader_trades = [trade for trade in structured_trader_trades if trade is not None]
    logger.info(f"Structured {len(structured_trader_trades)} trades.")

    # Step 3: Extract relevant tokens
    logger.info("Extracting relevant tokens...")
    tokens = get_tokens(structured_trader_trades)
    logger.info(f"Amount of unique tokens {len(tokens)}")

    relevant_tokens = await get_relevant_tokens(tokens, start_date=start_date, end_date=end_date)
    logger.info(f"Identified {len(relevant_tokens)} relevant tokens.")

    # Step 4: Filter out irrelevant trades
    logger.info("Filtering out irrelevant trades...")
    relevant_trades = filter_out_irrelevant_tokens(structured_trader_trades, relevant_tokens)
    logger.info(f"Filtered down to {len(relevant_trades)} relevant trades.")

    # Step 5: Add token launch date to trades
    logger.info("Adding launch date to trades...")
    enriched_trades = add_launch_time_to_trade(relevant_trades, relevant_tokens)
    logger.info(f"Added launch dates to {len(enriched_trades)} trades.")

    # Step 6: Create a DataFrame
    logger.info("Creating DataFrame from trades...")
    dataset = pd.DataFrame(enriched_trades)
    logger.info(f"Created dataset with {len(dataset)} rows.")

    write_data_to_cache(TOP_TRADER_TRADES_BIRDEYE, dataset)

    # Step 7: Return the dataset
    return dataset


def add_launch_time_to_trade(trades: List[dict], token_data: List[dict]) -> List[dict]:
    token_launch_data = {token["token"]: token[LAUNCH_DATE_COLUMN] for token in token_data}
    for trade in trades:
        trade[LAUNCH_DATE_COLUMN] = token_launch_data[trade["token"]]

    return trades


def filter_out_irrelevant_tokens(trades: List[dict], tokens: List[dict]) -> List[dict]:
    relevant_tokens = {token["token"]: True for token in tokens}
    relevant_trades = list()
    for trade in trades:
        if trade["token"] in relevant_tokens:
            relevant_trades.append(trade)
    return relevant_trades


def get_tokens(trades: List[dict]) -> List[str]:
    tokens = set()
    for trade in trades:
        tokens.add(trade["token"])

    return list(tokens)


async def get_relevant_tokens(tokens: List[str], start_date: datetime, end_date: datetime) -> List[dict]:
    relevant_tokens = []
    saved_token_info = select_token_creation_info_for_list(tokens)

    for index, token in enumerate(tokens):
        logger.info(f"Check if token is relevant {index + 1} of {len(tokens)}")

        if saved_token_info is not None and token in saved_token_info:
            create_info = saved_token_info[token]
        else:
            create_info = await get_token_create_info(token)

        result, launch_date = await check_token_create_info_date_range(token, start_date, end_date, create_info)

        if result:
            relevant_tokens.append({TOKEN_COlUMN: token, LAUNCH_DATE_COLUMN: launch_date})

    return relevant_tokens


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
    total_offset = 0

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
                # if offset >= 10000:
                #     offset = 0
                #     params["offset"] = offset

                data = await response.json()
                success, trades = validate_response(data, trader)
                if not success:
                    # todo add trader to blacklist as bot or split loading into more steps until 20k trades.
                    return []

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

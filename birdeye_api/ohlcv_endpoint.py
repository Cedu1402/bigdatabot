import logging
from datetime import datetime, timedelta
from typing import Optional

import aiohttp
import pandas as pd

from birdeye_api.api_limit import check_api_limit
from constants import BIRDEYE_KEY, TRADING_MINUTE_COLUMN, TOKEN_COlUMN, TOTAL_VOLUME_COLUMN, \
    PRICE_COLUMN
from env_data.get_env_value import get_env_value

logger = logging.getLogger(__name__)


def ohlcv_to_dataframe(result: dict) -> pd.DataFrame:
    items = result.get("data", {}).get("items", [])
    if not items:
        return pd.DataFrame()

    df = pd.DataFrame(items)
    df.rename(
        columns={
            "unixTime": TRADING_MINUTE_COLUMN,
            "v": TOTAL_VOLUME_COLUMN,
            "c": PRICE_COLUMN,
            "address": TOKEN_COlUMN,
        },
        inplace=True,
    )

    # Convert the Unix timestamp to a datetime object for trading minute
    df[TRADING_MINUTE_COLUMN] = pd.to_datetime(df[TRADING_MINUTE_COLUMN], unit='s')

    return df[[TOKEN_COlUMN, TRADING_MINUTE_COLUMN, TOTAL_VOLUME_COLUMN, PRICE_COLUMN]]


async def get_time_frame_ohlcv(token: str, trading_minute: datetime, window: int, interval: str) -> Optional[
    pd.DataFrame]:
    try:
        start = trading_minute - timedelta(minutes=window - 1)
        end = trading_minute

        data = await get_ohlcv(token, start, end, interval)

        return ohlcv_to_dataframe(data)
    except Exception as e:
        logger.exception("Failed to load ohlcv dataset", extra={"token": token, "trading_minute": trading_minute})
        return None


async def get_ohlcv(token: str, start_date: datetime, end_date: datetime, interval: str,
                    api_limit: bool = True) -> pd.DataFrame:
    """
       Fetches OHLCV (Open, High, Low, Close, Volume) data for a specific token within a given time range
       from the BirdEye API.

       Args:
           token (str): The token address for which to retrieve OHLCV data.
           start_date (datetime): The start date and time of the requested data range (UTC).
           end_date (datetime): The end date and time of the requested data range (UTC).
           interval (str): The interval type for the data (e.g., '1m', '5m', '1h', '1d').
           api_limit (bool): Checks if birdeye limit is reached or not.

       Returns:
           dict: The JSON response from the BirdEye API containing OHLCV data.

       Raises:
           Exception: If the BirdEye API request limit (50,000) is reached.
           aiohttp.ClientResponseError: If the API response has a non-2xx status code.

       Notes:
           - The BirdEye API provides OHLCV data for tokens on the Solana blockchain.
           - This function increments an API call counter in Redis (BIRD_EYE_COUNTER) and logs an error
             if the daily limit is exceeded.
           - Ensure that the Redis counter is initialized and properly configured before using this function.
       """

    url = "https://public-api.birdeye.so/defi/ohlcv"

    key = get_env_value(BIRDEYE_KEY)
    headers = {
        "accept": "application/json",
        "x-chain": "solana",
        "X-API-KEY": key,
    }
    params = {
        "address": token,
        "type": interval,
        "time_from": int(start_date.timestamp()),
        "time_to": int(end_date.timestamp())
    }

    await check_api_limit(api_limit)

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            response.raise_for_status()
            return await response.json()

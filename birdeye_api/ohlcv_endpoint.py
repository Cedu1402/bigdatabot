import logging
from datetime import datetime, timedelta

import aiohttp
import pandas as pd

from constants import BIRDEYE_KEY, TRADING_MINUTE_COLUMN, TOKEN_COlUMN, TOTAL_VOLUME_COLUMN, \
    PRICE_COLUMN
from env_data.get_env_value import get_env_value


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


async def get_time_frame_ohlcv(token: str, trading_minute: datetime, window: int, interval: str) -> pd.DataFrame:
    try:
        start = trading_minute - timedelta(minutes=window - 1)
        end = trading_minute

        data = await get_ohlcv(token, start, end, interval)

        return ohlcv_to_dataframe(data)
    except Exception as e:
        logging.error(e)
        return pd.DataFrame()


async def get_ohlcv(token: str, start_date: datetime, end_date: datetime, interval: str):
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

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            response.raise_for_status()
            return await response.json()

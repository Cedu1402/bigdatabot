from datetime import datetime
from typing import Tuple

import aiohttp

from birdeye_api.api_limit import check_api_limit
from constants import BIRDEYE_KEY
from data.redis_helper import get_async_redis
from env_data.get_env_value import get_env_value
from solana_api.solana_data import block_time_stamp_to_datetime


async def get_token_create_info(token: str, api_limit: bool = False) -> Tuple[datetime, str]:
    url = "https://public-api.birdeye.so/defi/token_creation_info"
    r = get_async_redis()

    key = get_env_value(BIRDEYE_KEY)
    headers = {
        "accept": "application/json",
        "x-chain": "solana",
        "X-API-KEY": key,
    }
    params = {
        "address": token
    }

    await check_api_limit(api_limit)

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            response.raise_for_status()  # Raises error if status is 4xx or 5xx
            result = await response.json()
            timestamp = result["data"]["blockUnixTime"]
            return block_time_stamp_to_datetime(timestamp), result["data"]["owner"]

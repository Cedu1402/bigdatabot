from datetime import datetime
from typing import Tuple

import aiohttp

from constants import BIRDEYE_KEY, BIRD_EYE_COUNTER
from data.redis_helper import get_async_redis
from env_data.get_env_value import get_env_value
from solana_api.solana_data import block_time_stamp_to_datetime


async def get_token_create_info(token: str) -> Tuple[datetime, str]:
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

    await r.incr(BIRD_EYE_COUNTER)
    counter = await r.get(BIRD_EYE_COUNTER)
    if counter is None:
        counter = 1
    if int(counter) >= 50000:
        raise Exception("Brideye limit reached!!!")

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            response.raise_for_status()  # Raises error if status is 4xx or 5xx
            result = await response.json()
            timestamp = result["data"]["blockUnixTime"]
            return block_time_stamp_to_datetime(timestamp), result["data"]["owner"]

from datetime import datetime

import aiohttp

from constants import BIRDEYE_KEY, BIRD_EYE_COUNTER
from data.redis_helper import get_redis_client
from env_data.get_env_value import get_env_value
from solana_api.solana_data import block_time_stamp_to_datetime


async def get_token_create_time(token: str) -> datetime:
    url = "https://public-api.birdeye.so/defi/token_creation_info"
    r = get_redis_client()

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
    if await r.get(BIRD_EYE_COUNTER) >= 50000:
        raise Exception("Brideye limit reached!!!")

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            response.raise_for_status()  # Raises error if status is 4xx or 5xx
            result = await response.json()
            timestamp = result["data"]["blockUnixTime"]
            return block_time_stamp_to_datetime(timestamp)

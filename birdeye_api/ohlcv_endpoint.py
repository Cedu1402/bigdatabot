from datetime import datetime

import aiohttp

from birdeye_api.api_key import get_api_key


async def get_ohlcv(token: str, start_date: datetime, end_date: datetime, interval: str):
    url = "https://public-api.birdeye.so/defi/ohlcv/pair"
    headers = {
        "accept": "application/json",
        "x-chain": "solana",
        "X-API-KEY": get_api_key(),
    }
    params = {
        "address": token,
        "type": interval,
        "time_from": start_date.timestamp(),
        "time_to": end_date.timestamp()
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            response.raise_for_status()  # Raises error if status is 4xx or 5xx
            return await response.json()
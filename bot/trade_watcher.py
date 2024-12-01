from asyncio import sleep
from datetime import datetime

import redis
from loguru import logger

from constants import GLOBAL_PROFIT_KEY, BAD_TRADES_KEY, DUMMY_INVESTMENT_AMOUNT, GOOD_TRADES_KEY
from solana_api.jupiter_api import get_token_price


async def watch_trade(token: str):
    # get current price
    buy_time = datetime.now()
    start_price = await get_token_price(token)
    last_price = None
    r = redis.Redis()

    await sleep(10)

    while True:
        if (datetime.now() - buy_time).total_seconds() >= 120 * 60:
            logger.info("Failed token because of time", start_price=start_price, last_price=last_price, token=token)
            await r.incrbyfloat(GLOBAL_PROFIT_KEY, - (DUMMY_INVESTMENT_AMOUNT / 2))
            await r.incr(BAD_TRADES_KEY)
            return

        last_price = await get_token_price(token)
        if last_price >= start_price * 1.10:  # 110% of start price
            logger.info(f"Price increased by 110%: {last_price} > {start_price * 1.10}", start_price=start_price,
                        last_price=last_price, token=token)

            await r.incrbyfloat(GLOBAL_PROFIT_KEY, DUMMY_INVESTMENT_AMOUNT)
            await r.incr(GOOD_TRADES_KEY)
            return

        if last_price <= start_price * 0.50:  # 50% of start price
            logger.info(f"Price decreased by 50%: {last_price} < {start_price * 0.50}", start_price=start_price,
                        last_price=last_price, token=token)
            await r.incrbyfloat(GLOBAL_PROFIT_KEY, - (DUMMY_INVESTMENT_AMOUNT / 2))
            await r.incr(BAD_TRADES_KEY)
            return

        await sleep(10)

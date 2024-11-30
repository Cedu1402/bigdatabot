from asyncio import sleep
from datetime import datetime

from log import logger
from solana_api.jupiter_api import get_token_price


async def watch_trade(token: str):
    # get current price
    buy_time = datetime.now()
    start_price = await get_token_price(token)
    last_price = None
    await sleep(10)

    while True:
        if (datetime.now() - buy_time).total_seconds() >= 120 * 60:
            logger.info("Failed token because of time", start_price, last_price)
            return

        last_price = await get_token_price(token)
        if last_price >= start_price * 1.10:  # 110% of start price
            logger.info(f"Price increased by 110%: {last_price} > {start_price * 1.10}")
            return

        if last_price <= start_price * 0.50:  # 50% of start price
            logger.info(f"Price decreased by 50%: {last_price} < {start_price * 0.50}")
            return

        await sleep(10)

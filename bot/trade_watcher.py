from asyncio import sleep
from datetime import datetime

from loguru import logger

from constants import DUMMY_INVESTMENT_AMOUNT, CURRENT_TRADE_WATCH_KEY
from data.redis_helper import get_redis_client, handle_failed_trade, handle_successful_trade, decrement_counter
from solana_api.jupiter_api import get_token_price


async def watch_trade(token: str):
    # get current price
    buy_time = datetime.now()
    start_price = await get_token_price(token)
    last_price = None
    r = get_redis_client()
    # Todo mark token as done
    await r.incr(CURRENT_TRADE_WATCH_KEY)
    await sleep(10)

    while True:
        try:
            if (datetime.now() - buy_time).total_seconds() >= 120 * 60:
                logger.info("Failed token because of time", start_price=start_price, last_price=last_price, token=token)
                await handle_failed_trade(r, token, DUMMY_INVESTMENT_AMOUNT / 2)
                return

            last_price = await get_token_price(token)
            if last_price >= start_price * 1.10:  # 110% of start price
                logger.info(f"Price increased by 110%: {last_price} > {start_price * 1.10}", start_price=start_price,
                            last_price=last_price, token=token)

                await handle_successful_trade(r, token, DUMMY_INVESTMENT_AMOUNT)
                return

            if last_price <= start_price * 0.50:  # 50% of start price
                logger.info(f"Price decreased by 50%: {last_price} < {start_price * 0.50}", start_price=start_price,
                            last_price=last_price, token=token)
                await handle_failed_trade(r, token, DUMMY_INVESTMENT_AMOUNT / 2)
                return
        except Exception as e:
            logger.exception("Error in trade watch", token=token)
        finally:
            await sleep(10)
            await decrement_counter(CURRENT_TRADE_WATCH_KEY, r)

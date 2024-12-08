import logging
from asyncio import sleep
from datetime import datetime

from dotenv import load_dotenv

from constants import DUMMY_INVESTMENT_AMOUNT, CURRENT_TRADE_WATCH_KEY
from data.redis_helper import get_async_redis, handle_failed_trade, handle_successful_trade, decrement_counter
from solana_api.jupiter_api import get_token_price
from structure_log.logger_setup import setup_logger

setup_logger("trade_watcher")
logger = logging.getLogger(__name__)


async def watch_trade(token: str):
    # get current price
    load_dotenv()
    logger.info("Start trade watcher", extra={"token": token})

    buy_time = datetime.now()
    start_price = await get_token_price(token)

    logger.info("Simulate buy of token",
                extra={"token": token, "start_price": start_price, "buy_time": buy_time.isoformat()})
    r = get_async_redis()

    await r.incr(CURRENT_TRADE_WATCH_KEY)
    await sleep(10)
    try:
        while True:
            try:

                # Calculate profit/loss percentage
                last_price = await get_token_price(token)
                price_change_percentage = (last_price - start_price) / start_price * 100
                profit = DUMMY_INVESTMENT_AMOUNT * (price_change_percentage / 100)

                if (datetime.now() - buy_time).total_seconds() >= 120 * 60:
                    logger.info(
                        "Failed token because of time",
                        extra={"start_price": start_price, "last_price": last_price, "token": token, "profit": profit}
                    )
                    await handle_failed_trade(r, token, DUMMY_INVESTMENT_AMOUNT / 2)
                    return

                if last_price >= start_price * 2.10:  # 110% of start price
                    logger.info(
                        f"Price increased by 110%",
                        extra={"start_price": start_price, "last_price": last_price, "token": token, "profit": profit}
                    )

                    await handle_successful_trade(r, token, DUMMY_INVESTMENT_AMOUNT)
                    return

                if last_price <= start_price * 0.50:  # 50% of start price
                    logger.info(
                        f"Price decreased by 50%: {last_price} < {start_price * 0.50}",
                        extra={"start_price": start_price, "last_price": last_price, "token": token, "profit": profit}
                    )
                    await handle_failed_trade(r, token, DUMMY_INVESTMENT_AMOUNT / 2)
                    return
            except Exception as e:
                logger.exception("Error in trade watch", extra={"token": token})
            finally:
                await sleep(10)
    except Exception as e:
        logger.exception("Failed to watch trade", extra={"token": token})
    finally:
        await decrement_counter(CURRENT_TRADE_WATCH_KEY, r)

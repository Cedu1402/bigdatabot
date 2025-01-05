import logging
from asyncio import sleep
from datetime import datetime

from dotenv import load_dotenv

from constants import INVESTMENT_AMOUNT, REAL_MONEY_MODE
from data.data_format import get_sol_price
from data.redis_helper import get_async_redis
from database.token_trade_history_table import insert_token_trade_history, update_sell_price
from dto.token_trade_history_model import TokenTradeHistory
from env_data.get_env_value import get_env_bool_value
from solana_api.jupiter_api import get_token_price_by_quote
from solana_api.trader import buy_token, sell_token
from structure_log.logger_setup import setup_logger

setup_logger("trade_watcher")
logger = logging.getLogger(__name__)


async def watch_trade(token: str):
    try:
        # get current price
        load_dotenv()
        logger.info("Start trade watcher", extra={"token": token})
        real_money_mode = get_env_bool_value(REAL_MONEY_MODE)
        buy_time = datetime.utcnow()
        r = get_async_redis()

        buy_amount, start_price = await buy_token(token, 120, 15, real_money_mode)
        if buy_amount is None or start_price is None:
            logger.error("Failed to buy/simulate token", extra={"token": token})
            return

        logger.info("Simulate buy of token/execute",
                    extra={"token": token, "start_price": str(start_price), "buy_time": buy_time.isoformat(),
                           "buy_amount": str(buy_amount)})

        insert_token_trade_history(TokenTradeHistory(token=token, buy_time=buy_time,
                                                     sell_time=None, buy_price=start_price,
                                                     sell_price=None))
        await sleep(10)

        while True:
            try:
                # Calculate profit/loss percentage
                sol_price = await get_sol_price(r)
                last_price, quote = await get_token_price_by_quote(token, buy_amount, False, sol_price)
                logger.info("Current price of token", extra={"token": token, "price": str(last_price)})

                price_change_percentage = (last_price - start_price) / start_price * 100
                profit = INVESTMENT_AMOUNT * (price_change_percentage / 100)

                if (datetime.now() - buy_time).total_seconds() >= 120 * 60:
                    if real_money_mode and buy_amount is not None:
                        await sell_token(token, buy_amount, 240, quote, False)

                    logger.info(
                        "Failed token because of time",
                        extra={"start_price": start_price, "last_price": last_price, "token": token, "profit": profit}
                    )
                    update_sell_price(token, last_price)
                    return

                if last_price >= start_price * 2.10:  # 110% of start price
                    if real_money_mode and buy_amount is not None:
                        sold_successful = await sell_token(token, buy_amount, 240, quote, True)
                        if not sold_successful:
                            logger.warning("Failed to sell token", extra={"token": token, "price": str(last_price)})
                            continue

                    logger.info(
                        f"Price increased by 110%",
                        extra={"start_price": start_price, "last_price": last_price, "token": token, "profit": profit}
                    )
                    update_sell_price(token, last_price)
                    return

                if last_price <= start_price * 0.50:  # 50% of start price
                    if real_money_mode and buy_amount is not None:
                        await sell_token(token, buy_amount, 240, quote, False)

                    logger.info(
                        f"Price decreased by 50%: {last_price} < {start_price * 0.50}",
                        extra={"start_price": start_price, "last_price": last_price, "token": token, "profit": profit}
                    )
                    update_sell_price(token, last_price)
                    return
            except Exception as e:
                logger.exception("Error in trade watch", extra={"token": token})
            finally:
                await sleep(10)
    except Exception as e:
        logger.exception("Failed to watch trade", extra={"token": token})

import logging
from asyncio import sleep
from datetime import datetime

from dotenv import load_dotenv

from constants import DUMMY_INVESTMENT_AMOUNT
from database.token_trade_history_table import insert_token_trade_history
from dto.token_trade_history_model import TokenTradeHistory
from solana_api.jupiter_api import get_token_price
from structure_log.logger_setup import setup_logger

setup_logger("trade_watcher")
logger = logging.getLogger(__name__)


async def watch_trade(token: str):
    # get current price
    load_dotenv()
    logger.info("Start trade watcher", extra={"token": token})

    buy_time = datetime.utcnow()
    start_price = await get_token_price(token)

    logger.info("Simulate buy of token",
                extra={"token": token, "start_price": start_price, "buy_time": buy_time.isoformat()})

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
                    insert_token_trade_history(TokenTradeHistory(token=token, buy_time=buy_time,
                                                                 sell_time=datetime.utcnow(), buy_price=start_price,
                                                                 sell_price=last_price))
                    return

                if last_price >= start_price * 2.10:  # 110% of start price
                    logger.info(
                        f"Price increased by 110%",
                        extra={"start_price": start_price, "last_price": last_price, "token": token, "profit": profit}
                    )
                    insert_token_trade_history(TokenTradeHistory(token=token, buy_time=buy_time,
                                                                 sell_time=datetime.utcnow(), buy_price=start_price,
                                                                 sell_price=last_price))
                    return

                if last_price <= start_price * 0.50:  # 50% of start price
                    logger.info(
                        f"Price decreased by 50%: {last_price} < {start_price * 0.50}",
                        extra={"start_price": start_price, "last_price": last_price, "token": token, "profit": profit}
                    )
                    insert_token_trade_history(TokenTradeHistory(token=token, buy_time=buy_time,
                                                                 sell_time=datetime.utcnow(), buy_price=start_price,
                                                                 sell_price=last_price))
                    return
            except Exception as e:
                logger.exception("Error in trade watch", extra={"token": token})
            finally:
                await sleep(10)
    except Exception as e:
        logger.exception("Failed to watch trade", extra={"token": token})

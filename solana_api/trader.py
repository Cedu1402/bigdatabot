import logging
from asyncio import sleep
from datetime import datetime
from typing import Optional

from constants import INVESTMENT_AMOUNT
from data.data_format import get_sol_price
from data.redis_helper import get_async_redis
from solana_api.jupiter_api import get_quote, get_token_price

logger = logging.getLogger(__name__)


async def buy_token(token: str, max_retry_time: int, max_higher_price: int) -> Optional[int]:
    try:
        r = get_async_redis()
        current_sol_price = await get_sol_price(r)
        sol_to_invest = INVESTMENT_AMOUNT / current_sol_price
        logger.info("Calculated sol to invest", extra={"sol_to_invest": sol_to_invest})
        start_price = await get_token_price(token)
        start_time = datetime.utcnow()

        while True:
            if (datetime.utcnow() - start_time).seconds > max_retry_time:
                return None

            logger.info("Fetching quote for token %s with amount %d", token, sol_to_invest)
            quote_response = await get_quote(token, sol_to_invest, True)
            if quote_response is None:
                logger.error("Failed to fetch quote.")
                await sleep(5)





    except Exception as e:
        logger.exception("Failed to buy token", extra={"token": token})

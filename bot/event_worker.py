import json
import logging
from datetime import datetime

import redis
from loguru import logger
from rq import Queue
from solders.pubkey import Pubkey

from birdeye_api.token_creation_endpoint import get_token_create_time
from bot.token_watcher import watch_token
from constants import TOKEN_QUEUE, CREATE_PREFIX, TRADE_PREFIX
from solana_api.solana_data import get_user_trades_in_block


async def handle_user_event(event):
    try:
        r = redis.Redis()
        queue = Queue(TOKEN_QUEUE, connection=r)

        trader, data = event
        logging.info(f"Received change for trader {trader}")
        slot = data["params"]["result"]["context"]["slot"]

        trades = await get_user_trades_in_block(Pubkey.from_string(trader), slot, "https://api.mainnet-beta.solana.com")
        if len(trades) == 0:
            return

        logging.info(f"Trade found for trader {trader}")
        for trade in trades:
            # check if coin is in list already
            token_exist = r.exists(trade.token)
            # check if buy was over 1 sol
            if not token_exist and trade.buy and abs(trade.sol_amount) < 1000000000:
                logger.info("Buy was not over one sol", trade=trade)
                continue

            token_create_time = r.get(CREATE_PREFIX + trade.token)
            if token_create_time is None:
                try:
                    token_create_time = await get_token_create_time(trade.token)
                    await r.set(CREATE_PREFIX + trade.token, token_create_time.isoformat())
                except Exception as e:
                    logger.exception(f"Failed to get token create time")

            if (datetime.utcnow() - token_create_time).total_seconds() > 120 * 60:
                logger.info("Token older than two horus, skip", trade=trade)
                continue

            # add coin to list if not
            await r.lpush(TRADE_PREFIX + trade.token, json.dumps(trade))

            if not token_exist:
                # Enqueue a task with some data
                logger.info("Add token to token watch", trade=trade)
                queue.enqueue(watch_token, trade.token)

    except Exception as e:
        logging.exception("Failed to process message")

import json
import logging
from datetime import datetime

from loguru import logger
from rq import Queue
from solders.pubkey import Pubkey

from birdeye_api.token_creation_endpoint import get_token_create_time
from bot.token_watcher import watch_token
from constants import TOKEN_QUEUE, CREATE_PREFIX, TRADE_PREFIX, CURRENT_EVENT_WATCH_KEY
from data.redis_helper import get_redis_client, decrement_counter
from env_data.get_env_value import get_env_value
from main import SOL_RPC
from solana_api.solana_data import get_user_trades_in_block


async def handle_user_event(event):
    r = get_redis_client()
    try:
        queue = Queue(TOKEN_QUEUE, connection=r)
        await r.incr(CURRENT_EVENT_WATCH_KEY)

        trader, data = event
        logging.info(f"Received change for trader {trader}")
        slot = data["params"]["result"]["context"]["slot"]

        solana_rpc = get_env_value(SOL_RPC)

        trades = await get_user_trades_in_block(Pubkey.from_string(trader), slot, solana_rpc)
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
    finally:
        await decrement_counter(CURRENT_EVENT_WATCH_KEY, r)

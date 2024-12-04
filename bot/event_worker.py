import json
from datetime import datetime

from dotenv import load_dotenv
from rq import Queue
from solders.pubkey import Pubkey

from birdeye_api.token_creation_endpoint import get_token_create_time
from bot.token_watcher import watch_token
from constants import TOKEN_QUEUE, CREATE_PREFIX, TRADE_PREFIX, CURRENT_EVENT_WATCH_KEY, SOL_RPC
from data.redis_helper import get_async_redis, decrement_counter, get_sync_redis
from env_data.get_env_value import get_env_value
from solana_api.solana_data import get_user_trades_in_block
from structure_log.logger_setup import logger


async def handle_user_event(event):
    r = get_async_redis()
    load_dotenv()

    try:
        queue = Queue(TOKEN_QUEUE, connection=get_sync_redis(), default_timeout=19000)
        await r.incr(CURRENT_EVENT_WATCH_KEY)

        trader, data = event
        logger.info(f"Received change for trader {trader}", trader=trader)
        slot = data["params"]["result"]["context"]["slot"]

        solana_rpc = get_env_value(SOL_RPC)
        trades = await get_user_trades_in_block(Pubkey.from_string(trader), slot, solana_rpc)
        if len(trades) == 0:
            logger.info(f"No trades found for {trader} {slot}", trader=trader, slot=slot)
            return

        logger.info(f"Trade found for trader {trader}", trader=trader)
        for trade in trades:
            # check if coin is in list already
            token_exist = await r.exists(trade.token)
            # # check if buy was over 1 sol
            # if not token_exist and trade.buy and abs(trade.sol_amount) < 1000000000:
            #     logger.info("Buy was not over one sol", trade=trade)
            #     continue

            token_create_time = await r.get(CREATE_PREFIX + trade.token)
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
        logger.exception("Failed to process message")
    finally:
        await decrement_counter(CURRENT_EVENT_WATCH_KEY, r)

import json
from datetime import datetime
from typing import Dict

import redis.asyncio
from dotenv import load_dotenv
from rq import Queue
from solders.pubkey import Pubkey

from birdeye_api.token_creation_endpoint import get_token_create_time
from bot.token_watcher import watch_token
from constants import TOKEN_QUEUE, CREATE_PREFIX, TRADE_PREFIX, CURRENT_EVENT_WATCH_KEY, SOL_RPC, SUBSCRIPTION_MAP
from data.redis_helper import get_async_redis, decrement_counter, get_sync_redis
from env_data.get_env_value import get_env_value
from solana_api.solana_data import get_latest_user_trade
from structure_log.logger_setup import logger, setup_logger


async def check_token_create_time(r: redis.asyncio.Redis, token: str) -> bool:
    token_create_time = await r.get(CREATE_PREFIX + token)
    if token_create_time is None:
        try:
            token_create_time = await get_token_create_time(token)
            await r.set(CREATE_PREFIX + token, token_create_time.isoformat())
        except Exception as e:
            logger.exception(f"Failed to get token create time")
            return False
    else:
        token_create_time = datetime.fromisoformat(token_create_time)

    if (datetime.utcnow() - token_create_time).total_seconds() > 120 * 60:
        logger.info("Token older than two horus, skip", token=token)
        return False

    return True


async def get_subscription_map(r: redis.asyncio.Redis) -> Dict[int, str]:
    subscription_map = await r.get(SUBSCRIPTION_MAP)
    if subscription_map is None:
        return dict()
    logger.debug("Raw subscription_map", subscription_map=str(subscription_map))
    subscription_map = json.loads(subscription_map)
    logger.debug("Parsed subscription_map", subscription_map=subscription_map)
    subscription_map = {int(key): value for key, value in subscription_map.items()}
    logger.info("Loaded subscription map from redis")
    return subscription_map


async def handle_user_event(event):
    r = get_async_redis()
    load_dotenv()
    setup_logger("event_worker")
    try:
        subscription_map = await get_subscription_map(r)
        data = json.loads(event)
        sub_id = data["params"]["subscription"]
        logger.info("Trader id form event", sub_id=sub_id)
        trader = subscription_map.get(sub_id, None)
        if trader is None:
            logger.error("Trader not found in map", sub_id=sub_id, subscription_map=subscription_map)
        logger.info(f"Received wallet action {trader}", data=data, trader=trader)

        queue = Queue(TOKEN_QUEUE, connection=get_sync_redis(), default_timeout=19000)
        await r.incr(CURRENT_EVENT_WATCH_KEY)

        solana_rpc = get_env_value(SOL_RPC)
        trade = await get_latest_user_trade(Pubkey.from_string(trader), solana_rpc)
        if trade is None:
            logger.info(f"No trades found for {trader}", trader=trader)
            return

        logger.info(f"Trade found for trader {trader}", trader=trader)
        # check if coin is in list already
        token_exist = await r.exists(trade.token)

        if not (await check_token_create_time(r, trade.token)):
            return

        # # check if buy was over 1 sol
        # if not token_exist and trade.buy and abs(trade.sol_amount) < 1000000000:
        #     logger.info("Buy was not over one sol", trade=trade)
        #     continue

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

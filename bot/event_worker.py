import json
from datetime import datetime
from typing import Dict, Optional, Tuple

import redis.asyncio
from dotenv import load_dotenv
from rq import Queue
from solders.pubkey import Pubkey

from birdeye_api.token_creation_endpoint import get_token_create_info
from bot.token_watcher import watch_token
from constants import TOKEN_QUEUE, CREATE_PREFIX, TRADE_PREFIX, CURRENT_EVENT_WATCH_KEY, SOL_RPC, SUBSCRIPTION_MAP, \
    PUMP_DOT_FUN_AUTHORITY, TOKEN_WATCHER_KEY
from data.redis_helper import get_async_redis, decrement_counter, get_sync_redis
from env_data.get_env_value import get_env_value
from solana_api.solana_data import get_latest_user_trade
from structure_log.logger_setup import logger, setup_logger, ensure_logging_flushed

setup_logger("event_worker")

async def load_token_create_info(token: str, r: redis.asyncio.Redis) -> Optional[Tuple[datetime, str]]:
    try:
        token_create_time, owner = await get_token_create_info(token)
        await r.set(CREATE_PREFIX + token, json.dumps((token_create_time.isoformat(), owner)))
        return token_create_time, owner
    except Exception as e:
        logger.exception(f"Failed to get token create time")
        return None


async def check_token_create_info(r: redis.asyncio.Redis, token: str) -> bool:
    token_create_info = await r.get(CREATE_PREFIX + token)
    if token_create_info is None:
        token_create_info = await load_token_create_info(token, r)
        if token_create_info is None:
            logger.info("Failed to load token create info")
            return False
        token_create_time, owner = token_create_info
    else:
        token_create_time, owner = json.loads(token_create_info)
        token_create_time = datetime.fromisoformat(token_create_time)

    if owner != PUMP_DOT_FUN_AUTHORITY:
        logger.info("Not a pump fun token", token=token, owner=owner)
        return False

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


def get_trader_form_event(event, subscription_map: Dict[int, str]) -> Optional[str]:
    data = json.loads(event)
    sub_id = data["params"]["subscription"]
    logger.info("Trader id form event", sub_id=sub_id)
    trader = subscription_map.get(sub_id, None)
    if trader is None:
        logger.error("Trader not found in map", sub_id=sub_id, subscription_map=subscription_map)
        return None

    logger.info(f"Received wallet action {trader}", data=data, trader=trader)
    return trader


def setup_handler() -> Tuple[redis.asyncio.Redis, Queue]:
    logger.info("Start of event worker task")

    r = get_async_redis()
    load_dotenv()

    queue = Queue(TOKEN_QUEUE, connection=get_sync_redis(), default_timeout=19000)
    return r, queue


async def handle_user_event(event):
    r, queue = setup_handler()

    try:
        subscription_map = await get_subscription_map(r)
        trader = get_trader_form_event(event, subscription_map)

        await r.incr(CURRENT_EVENT_WATCH_KEY)

        solana_rpc = get_env_value(SOL_RPC)
        trade = await get_latest_user_trade(Pubkey.from_string(trader), solana_rpc)
        if trade is None:
            logger.info(f"No trades found for {trader}", trader=trader)
            return

        logger.info(f"Trade found for trader {trader}", trader=trader)

        # check if coin is in list already
        token_watch_redis_key = TOKEN_WATCHER_KEY + "_" + trade.token
        token_exist = bool(await r.exists(token_watch_redis_key))
        logger.info("Token already in list", token_exist=token_exist)

        if not (await check_token_create_info(r, trade.token)):
            return

        await r.lpush(TRADE_PREFIX + trade.token, json.dumps(trade.to_dict()))
        logger.info("Token trade added to list", trade=trade.to_dict())

        # add coin to list if not
        if not token_exist:
            # Enqueue a task with some data
            logger.info("Add token to token watch", trade=trade.to_dict())
            queue.enqueue(watch_token, trade.token)
            await r.set(token_watch_redis_key, json.dumps(True))

    except Exception as e:
        logger.exception("Failed to process message")
    finally:
        await decrement_counter(CURRENT_EVENT_WATCH_KEY, r)
        ensure_logging_flushed()

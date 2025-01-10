import json
import logging
from datetime import datetime
from typing import Dict, Optional, Tuple

import redis.asyncio
from dotenv import load_dotenv
from rq import Queue
from solders.pubkey import Pubkey

from blockchain_token.token_creation import check_token_create_info_age_now
from bot.token_watcher import watch_token
from constants import TOKEN_QUEUE, SOL_RPC, SUBSCRIPTION_MAP
from data.redis_helper import get_async_redis, get_sync_redis
from database.event_table import insert_event
from database.token_watch_table import token_watch_exists
from database.trade_table import insert_trade
from env_data.get_env_value import get_env_value
from solana_api.solana_data import get_latest_user_trade
from structure_log.logger_setup import setup_logger, ensure_logging_flushed

setup_logger("event_worker")
logger = logging.getLogger(__name__)


async def get_subscription_map(r: redis.asyncio.Redis) -> Optional[Dict[int, str]]:
    try:
        subscription_map = await r.get(SUBSCRIPTION_MAP)
        if subscription_map is None:
            return None

        logger.debug("Raw subscription_map", extra={"subscription_map": str(subscription_map)})
        subscription_map = json.loads(subscription_map)
        logger.debug("Parsed subscription_map", extra={"subscription_map": str(subscription_map)})
        subscription_map = {int(key): value for key, value in subscription_map.items()}
        logger.info("Loaded subscription map from redis")
        return subscription_map
    except Exception as e:
        logger.exception(f"Failed to get subscription map")
        return None


async def get_trader_form_event(event) -> Optional[str]:
    data = json.loads(event)
    r = get_async_redis()
    sub_id = data["params"]["subscription"]
    logger.info("Trader id form event", extra={"sub_id": sub_id})

    subscription_map = await get_subscription_map(r)
    if subscription_map is None:
        logger.error("Subscription map not found in redis", extra={"sub_id": sub_id})
        return None

    if sub_id not in subscription_map:
        logger.error("Id not found in map", extra={"sub_id": sub_id})

    trader = subscription_map[sub_id]
    logger.info(f"Received wallet action {trader}", extra={"data": data, "trader": trader})

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
        trader = await get_trader_form_event(event)
        insert_event(trader if trader is not None else "FAILED", datetime.utcnow(), "")
        if trader is None:
            return

        solana_rpc = get_env_value(SOL_RPC)
        trade = await get_latest_user_trade(Pubkey.from_string(trader), solana_rpc)
        if trade is None:
            logger.info(f"No trades found for {trader}", extra={"trader": trader})
            return

        logger.info(f"Trade found for trader {trader}", extra={"trader": trader})

        # check if coin is in list already
        token_is_watched = token_watch_exists(trade.token)
        logger.info("Token already in list", extra={"token_exist": token_is_watched})

        result = await check_token_create_info_age_now(trade.token)
        logger.info(f"check_token_create_info returned", extra={"result": result})
        if not result:
            logger.info("Skip token create info check is false")
            return

        insert_trade(trade)
        logger.info("Token trade added to list", extra={"trade": trade.to_dict()})

        # add coin to list if not
        if not token_is_watched:
            # Enqueue a task with some data
            logger.info("Add token to token watch", extra={"trade": trade.to_dict()})
            queue.enqueue(watch_token, trade.token)

    except Exception as e:
        logger.exception("Failed to process message")
    finally:
        logger.info("Finished watch task clean up and exit.")
        ensure_logging_flushed()

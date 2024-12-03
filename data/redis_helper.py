import redis
from structure_log.logger_setup import logger

from constants import REDIS_URL, BAD_TRADES_KEY, BAD_TOKENS_KEY, GOOD_TRADES_KEY, \
    GOOD_TOKENS_KEY, GLOBAL_PROFIT_KEY
from env_data.get_env_value import get_env_value


def get_redis_url() -> str:
    redis_url = get_env_value(REDIS_URL)
    if redis_url is None:
        redis_url = 'localhost'

    return redis_url


def get_async_redis() -> redis.asyncio.Redis:
    return redis.asyncio.Redis(host=get_redis_url(), port=6379, db=0)


def get_sync_redis() -> redis.Redis:
    return redis.Redis(host=get_redis_url(), port=6379, db=0)


async def decrement_counter(key: str, r: redis.Redis):
    try:
        await r.decr(key)
    except Exception as e:
        logger.exception("Failed to decrement counter", key=key)


async def update_global_profit(r, amount: float):
    await r.incrbyfloat(GLOBAL_PROFIT_KEY, amount)


async def increment_counter(r, key: str):
    await r.incr(key)


async def add_to_redis_list(r, list_key: str, value: str):
    await r.rpush(list_key, value)


async def handle_failed_trade(r, token: str, loss: float):
    await update_global_profit(r, -loss)
    await increment_counter(r, BAD_TRADES_KEY)
    await add_to_redis_list(r, BAD_TOKENS_KEY, token)


async def handle_successful_trade(r, token: str, profit: float):
    await update_global_profit(r, profit)
    await increment_counter(r, GOOD_TRADES_KEY)
    await add_to_redis_list(r, GOOD_TOKENS_KEY, token)

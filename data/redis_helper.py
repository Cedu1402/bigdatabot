import logging

import redis

from constants import REDIS_URL
from env_data.get_env_value import get_env_value

logger = logging.getLogger(__name__)


def get_redis_url() -> str:
    redis_url = get_env_value(REDIS_URL)
    if redis_url is None:
        redis_url = 'localhost'

    return redis_url


def get_async_redis() -> redis.asyncio.Redis:
    return redis.asyncio.Redis(host=get_redis_url(), port=6379, db=0)


def get_sync_redis() -> redis.Redis:
    return redis.Redis(host=get_redis_url(), port=6379, db=0)

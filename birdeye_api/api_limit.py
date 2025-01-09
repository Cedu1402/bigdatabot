import logging

from constants import BIRD_EYE_COUNTER
from data.redis_helper import get_async_redis

logger = logging.getLogger(__name__)


async def check_api_limit(check_limit: bool) -> bool:
    if not check_limit:
        return True

    r = get_async_redis()

    await r.incr(BIRD_EYE_COUNTER)

    counter = await r.get(BIRD_EYE_COUNTER)

    if counter is None:
        counter = 1

    if int(counter) >= 50000:
        logger.error("Brideye limit reached!!!")
        raise Exception("Brideye limit reached!!!")

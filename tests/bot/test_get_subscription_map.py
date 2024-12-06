import unittest

from bot.event_worker import get_subscription_map
from data.redis_helper import get_async_redis


class TestRunner(unittest.IsolatedAsyncioTestCase):


    async def test_get_subscription_map(self):
        r = get_async_redis()

        actual = await get_subscription_map(r)

        self.assertEqual(actual, {})
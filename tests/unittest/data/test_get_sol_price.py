import unittest
from unittest.mock import AsyncMock

from redis.asyncio import Redis

from data.data_format import get_sol_price


class TestGetSolPrice(unittest.IsolatedAsyncioTestCase):

    async def test_get_sol_price_with_value(self):
        # Mock Redis
        mock_redis = AsyncMock(spec=Redis)
        mock_redis.get = AsyncMock(return_value="200")

        # Call the function
        result = await get_sol_price(mock_redis)

        # Assert
        self.assertEqual(result, 200.0)
        mock_redis.get.assert_called_once_with("SOLANA_PRICE")

    async def test_get_sol_price_default_value(self):
        # Mock Redis
        mock_redis = AsyncMock(spec=Redis)
        mock_redis.get = AsyncMock(return_value=None)

        # Call the function
        result = await get_sol_price(mock_redis)

        # Assert
        self.assertEqual(result, 150.0)
        mock_redis.get.assert_called_once_with("SOLANA_PRICE")


if __name__ == "__main__":
    unittest.main()

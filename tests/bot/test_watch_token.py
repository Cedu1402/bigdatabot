import unittest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch, AsyncMock

import pandas as pd

from bot.token_watcher import watch_token
from constants import CREATE_PREFIX, PRICE_COLUMN, TOTAL_VOLUME_COLUMN, TRADING_MINUTE_COLUMN, TOKEN_COlUMN
from solana_api.trade_model import Trade


class TestRunner(unittest.IsolatedAsyncioTestCase):

    @patch("bot.token_watcher.get_valid_trades_of_token")
    @patch("bot.token_watcher.get_base_data")
    @patch("bot.token_watcher.get_sol_price")
    @patch("bot.token_watcher.check_if_token_done")
    @patch("bot.token_watcher.redis.asyncio.Redis")
    @patch("bot.token_watcher.Queue")
    async def test_watch_token(self,
                               mock_queue,
                               mock_async_redis,
                               token_done,
                               mock_get_sol_price,
                               mock_get_base_data,
                               mock_get_valid_trades):
        # Mock Redis
        mock_redis_instance = AsyncMock()
        mock_async_redis.return_value = mock_redis_instance
        mock_redis_instance.get.return_value = ((datetime.utcnow() - timedelta(hours=1)).isoformat(), "test")
        mock_redis_instance.incr.return_value = None  # Simulate successful increment
        mock_redis_instance.set.return_value = None

        # token done check
        token_done.return_value = False

        # Mock Queue
        mock_queue_instance = MagicMock()
        mock_queue.return_value = mock_queue_instance

        # Mock get_valid_trades_of_token
        mock_get_valid_trades.return_value = [
            Trade("1", "2", 1, 1, True, 1, (datetime.utcnow() - timedelta(hours=1)).isoformat())]

        # Mock get_base_data
        mock_get_base_data.return_value = pd.DataFrame(
            {
                "trader_DTkBYcYfQsZhDM9ZWk76GqdnwMpaGrc3uC9n6bq6rYp2_state": [1, 2, 3],
                "trader_2ekUyRWdrZ9eAoYeCAYYDVCzUwWaWcPyf2LdpVbUkNXd_state": [0, 1, 0],
                TOKEN_COlUMN: ["SOL", "SOL", "SOL"],
                TRADING_MINUTE_COLUMN: pd.date_range("2024-12-01 00:00:00", periods=3, freq="min"),
                TOTAL_VOLUME_COLUMN: [100, 200, 300],
                PRICE_COLUMN: [10.0, 10.5, 11.0],
            }
        )

        # Mock get_sol_price
        mock_get_sol_price.return_value = 20.0

        # Run the function
        result = await watch_token("SOL")

        # Assertions
        self.assertTrue(result)  # Expect True because of a buy signal
        mock_redis_instance.get.assert_called_with(CREATE_PREFIX + "SOL")
        mock_get_valid_trades.assert_called_once()
        mock_get_base_data.assert_called_once()
        mock_get_sol_price.assert_called_once()

    @patch("bot.token_watcher.get_valid_trades_of_token")
    @patch("bot.token_watcher.check_if_token_done")
    @patch("bot.token_watcher.redis.asyncio.Redis")
    async def test_token_done(self, mock_async_redis, mock_token_done, mock_get_valid_trades):
        # Mock Redis
        mock_redis_instance = AsyncMock()
        mock_async_redis.return_value = mock_redis_instance

        # Token done check
        mock_token_done.return_value = True  # Token is done, should exit early

        # Run the function
        result = await watch_token("SOL")

        # Assertions
        self.assertFalse(result)  # Expect False because token is already done
        mock_token_done.assert_called_once()

    @patch("bot.token_watcher.get_valid_trades_of_token")
    @patch("bot.token_watcher.check_if_token_done")
    @patch("bot.token_watcher.check_age_of_token")
    @patch("bot.token_watcher.redis.asyncio.Redis")
    async def test_token_age(self, mock_async_redis, mock_token_done, mock_check_age, mock_get_valid_trades):
        # Mock Redis
        mock_redis_instance = AsyncMock()
        mock_async_redis.return_value = mock_redis_instance
        mock_redis_instance.get.return_value = ((datetime.utcnow() - timedelta(hours=1)).isoformat(), "test")

        # Token done check
        mock_token_done.return_value = False

        # Token is older than 4 hours, should exit early
        mock_check_age.return_value = False

        # Run the function
        result = await watch_token("SOL")

        # Assertions
        self.assertFalse(result)  # Expect False because token is too old
        mock_check_age.assert_called_once()

if __name__ == "__main__":
    unittest.main()

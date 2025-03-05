import unittest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch, AsyncMock

import pandas as pd

from bot.token_watcher import watch_token
from constants import PRICE_COLUMN, TOTAL_VOLUME_COLUMN, TRADING_MINUTE_COLUMN, TOKEN_COLUMN, LAUNCH_DATE_COLUMN
from dto.trade_model import Trade


class TestRunner(unittest.IsolatedAsyncioTestCase):

    @patch("bot.token_watcher.get_valid_trades_of_token")
    @patch("bot.token_watcher.get_base_data")
    @patch("bot.token_watcher.check_if_token_done")
    @patch("bot.token_watcher.Queue")
    @patch("bot.token_watcher.insert_token_watch")
    @patch("bot.token_watcher.set_end_time")
    @patch("bot.token_watcher.select_token_creation_info")
    @patch("bot.token_watcher.insert_token_dataset")
    async def test_watch_token(self,
                               mock_insert_token_dataset,
                               mock_select_token_creation_info,
                               mock_set_end_time,
                               mock_insert_token_watch,
                               mock_queue,
                               token_done,
                               mock_get_base_data,
                               mock_get_valid_trades):
        # Mock Redis
        mock_select_token_creation_info.return_value = ((datetime.utcnow() - timedelta(hours=1)), "test")

        # token done check
        token_done.return_value = False

        # Mock Queue
        mock_queue_instance = MagicMock()
        mock_queue.return_value = mock_queue_instance

        # Mock get_valid_trades_of_token
        mock_get_valid_trades.return_value = [
            Trade("1", "2", 1, 1, True, 1, (datetime.utcnow() - timedelta(hours=1)).isoformat(), "")]

        # Mock get_base_data
        mock_get_base_data.return_value = pd.DataFrame(
            {
                TOKEN_COLUMN: ["SOL", "SOL", "SOL"],
                TRADING_MINUTE_COLUMN: pd.date_range("2024-12-01 00:00:00", periods=3, freq="min"),
                LAUNCH_DATE_COLUMN: pd.to_datetime("2024-11-30 00:00:00"),
                TOTAL_VOLUME_COLUMN: [100, 200, 300],
                PRICE_COLUMN: [10.0, 10.5, 11.0],
            }
        )

        # Run the function
        result = await watch_token("SOL")

        # Assertions
        self.assertTrue(result)
        mock_get_valid_trades.assert_called_once()
        mock_get_base_data.assert_called_once()
        mock_insert_token_watch.assert_called_once()
        mock_set_end_time.assert_called_once()

    @patch("bot.token_watcher.check_if_token_done")
    @patch("bot.token_watcher.redis.asyncio.Redis")
    async def test_token_done(self, mock_async_redis, mock_token_done):
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

    @patch("bot.token_watcher.check_if_token_done")
    @patch("bot.token_watcher.check_age_of_token")
    @patch("bot.token_watcher.redis.asyncio.Redis")
    @patch("bot.token_watcher.select_token_creation_info")
    @patch("bot.token_watcher.insert_token_watch")
    @patch("bot.token_watcher.set_end_time")
    async def test_token_age(self, mock_set_end_time, mock_insert_token_watch, mock_select_token_creation_info,
                             mock_async_redis, mock_token_done, mock_check_age):
        # Mock Redis
        mock_redis_instance = AsyncMock()
        mock_async_redis.return_value = mock_redis_instance
        mock_select_token_creation_info.return_value = ((datetime.utcnow() - timedelta(hours=1)), "test")

        # Token done check
        mock_token_done.return_value = False

        # Token is older than 4 hours, should exit early
        mock_check_age.return_value = False

        # Run the function
        result = await watch_token("SOL")

        # Assertions
        self.assertFalse(result)  # Expect False because token is too old
        mock_check_age.assert_called_once()
        mock_set_end_time.assert_called_once()
        mock_insert_token_watch.assert_called_once()


if __name__ == "__main__":
    unittest.main()

import unittest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

from bot.event_worker import handle_user_event
from constants import CREATE_PREFIX, TRADE_PREFIX


class TestRunner(unittest.IsolatedAsyncioTestCase):
    @patch("bot.event_worker.get_async_redis")
    @patch("bot.event_worker.get_sync_redis")
    @patch("bot.event_worker.Queue")
    async def test_handle_user_event(
            self, mock_queue, mock_get_sync_redis, mock_get_async_redis
    ):
        # Mock Redis and RQ objects
        mock_async_redis = AsyncMock()
        mock_sync_redis = MagicMock()
        mock_queue_instance = MagicMock()
        mock_get_async_redis.return_value = mock_async_redis
        mock_get_sync_redis.return_value = mock_sync_redis
        mock_queue.return_value = mock_queue_instance

        # Set up test data
        trader = "B5QzGuMknM2jTwUPzTBL4SbV6Zta6VAGMpTADCkbiwAq"
        event = (trader, {"params": {"result": {"context": {"slot": 305072709}}}})
        mock_async_redis.exists.return_value = False
        mock_async_redis.get.return_value = None

        # Call the function
        await handle_user_event(event)

        # Assertions for Redis interactions
        mock_async_redis.incr.assert_called_once_with("CURRENT_EVENT_WATCH_KEY")

        # Ensure counter was decremented
        mock_async_redis.decr.assert_called_once_with("CURRENT_EVENT_WATCH_KEY")

    @patch("your_module.get_async_redis")
    @patch("your_module.get_sync_redis")
    @patch("your_module.get_user_trades_in_block")
    async def test_no_trades_found(
            self, mock_get_user_trades_in_block, mock_get_async_redis
    ):
        mock_async_redis = AsyncMock()
        mock_get_async_redis.return_value = mock_async_redis
        mock_get_user_trades_in_block.return_value = []

        trader = "trader_pubkey"
        event = (trader, {"params": {"result": {"context": {"slot": 12345}}}})

        await handle_user_event(event)

        # No trades, should not enqueue or call lpush
        mock_async_redis.lpush.assert_not_called()
        mock_async_redis.exists.assert_not_called()

        # Ensure counter was decremented
        mock_async_redis.decr.assert_called_once_with("CURRENT_EVENT_WATCH_KEY")


if __name__ == "__main__":
    unittest.main()

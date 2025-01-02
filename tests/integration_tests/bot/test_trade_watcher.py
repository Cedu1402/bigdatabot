import unittest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch

from dotenv import load_dotenv

from bot.trade_watcher import watch_trade


class TestRunner(unittest.IsolatedAsyncioTestCase):

    @patch("bot.trade_watcher.insert_token_trade_history")
    @patch("solana_api.trader.get_sol_price", new_callable=AsyncMock)
    @patch("bot.trade_watcher.get_env_bool_value")
    @patch("bot.trade_watcher.get_async_redis")
    @patch("bot.trade_watcher.get_sol_price", new_callable=AsyncMock)
    async def test_watch_trade(
            self,
            mock_get_sol_price,
            mock_get_async_redis,
            mock_get_env_bool_value,
            mock_get_sol_price_2,
            mock_insert_token_trade_history
    ):
        load_dotenv()
        # Mock Redis
        mock_redis = AsyncMock()
        mock_get_async_redis.return_value = mock_redis
        mock_redis.get.return_value = 190

        # Mock other dependencies
        mock_get_sol_price.return_value = 190  # Mocked SOL price
        mock_get_sol_price_2.return_value = 190

        mock_get_env_bool_value.return_value = False

        # Mock timestamp for testing
        now = datetime.utcnow()
        mock_buy_time = now - timedelta(minutes=5)

        with patch("bot.trade_watcher.datetime") as mock_datetime:
            mock_datetime.utcnow.return_value = now

            # Call the function to test
            await watch_trade("9UTQN4PXGdpe9jd61the92M93nh3f5jUBq5kQiJypump")

            # Check Redis interaction
            mock_get_async_redis.assert_called_once()
            mock_redis.close.assert_called_once()

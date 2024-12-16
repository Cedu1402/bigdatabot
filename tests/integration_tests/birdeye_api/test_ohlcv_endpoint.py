import unittest
from datetime import datetime, timedelta
from unittest.mock import patch, AsyncMock

from dotenv import load_dotenv

from birdeye_api.ohlcv_endpoint import get_ohlcv, get_time_frame_ohlcv
from data.close_volume_data import get_trading_minute


class TestRunner(unittest.IsolatedAsyncioTestCase):
    @patch('birdeye_api.ohlcv_endpoint.get_async_redis')
    async def test_get_ohlcv_only_on_pump_fun(self, mock_redis):
        # Arrange
        mock_redis_instance = AsyncMock()
        mock_redis.return_value = mock_redis_instance
        load_dotenv()
        token = "4aR9JwW69Zy4nM8X46kGhSVuiYVTmMpN7bcATEwipump"
        start_date = datetime.utcnow()
        end_date = start_date + timedelta(minutes=10)
        interval = "1m"
        # Act
        actual = await get_ohlcv(token, start_date, end_date, interval)
        # Assert
        self.assertEqual(actual, [])

    @patch('birdeye_api.ohlcv_endpoint.get_async_redis')
    async def test_get_time_frame_ohlcv(self, mock_redis):
        # Arrange
        mock_redis_instance = AsyncMock()
        mock_redis.return_value = mock_redis_instance
        load_dotenv()
        token = "4aR9JwW69Zy4nM8X46kGhSVuiYVTmMpN7bcATEwipump"
        trading_minute = get_trading_minute()
        window = 11
        interval = "1m"
        # Act
        actual = await get_time_frame_ohlcv(token, trading_minute, window, interval)
        # Assert
        self.assertEqual(11, len(actual))

    @patch('birdeye_api.ohlcv_endpoint.get_async_redis')
    async def test_get_time_frame_ohlcv_4h(self, mock_redis):
        mock_redis_instance = AsyncMock()
        mock_redis.return_value = mock_redis_instance

        # Arrange
        load_dotenv()
        token = "4aR9JwW69Zy4nM8X46kGhSVuiYVTmMpN7bcATEwipump"
        trading_minute = get_trading_minute()
        window = 60 * 4
        interval = "1m"
        # Act
        actual = await get_time_frame_ohlcv(token, trading_minute, window, interval)
        # Assert
        self.assertEqual(60 * 4, len(actual))

import unittest
from datetime import datetime, timedelta

from dotenv import load_dotenv

from birdeye_api.ohlcv_endpoint import get_ohlcv


class TestRunner(unittest.IsolatedAsyncioTestCase):

    async def test_get_ohlcv_only_on_pump_fun(self):
        # Arrange
        load_dotenv()
        token = "Hzw7R5uxSGX1DiFLLq3TCz3tYmD52ZUwz6rtNMRPpump"
        start_date = datetime.now()
        end_date = start_date + timedelta(minutes=10)
        interval = "1m"
        # Act
        actual = await get_ohlcv(token, start_date, end_date, interval)
        # Assert
        self.assertEqual(actual, [])


import unittest
from datetime import datetime

from birdeye_api.ohlcv_endpoint import get_ohlcv


class TestRunner(unittest.TestCase):


    def test_get_ohlcv_only_on_pump_fun(self):
        # Arrange
        token = "Hzw7R5uxSGX1DiFLLq3TCz3tYmD52ZUwz6rtNMRPpump"
        start_date = datetime()

        # Act
        result = get_ohlcv(token)
        # Assert



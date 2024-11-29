import unittest
from datetime import datetime
from unittest.mock import patch

from data.close_volume_data import get_trading_minute


class TestRunner(unittest.TestCase):

    @patch("data.close_volume_data.datetime")
    def test_get_trading_minute(self, mock_datetime):
        # Arrange: Set a specific mocked time
        mock_now = datetime(2024, 11, 30, 15, 45, 23)
        mock_datetime.utcnow.return_value = mock_now

        # Act
        trading_minute = get_trading_minute()

        # Assert: Expected last full minute
        expected_trading_minute = datetime(2024, 11, 30, 15, 44)
        self.assertEqual(trading_minute, expected_trading_minute)

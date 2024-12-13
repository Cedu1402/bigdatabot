import unittest
from datetime import datetime
from unittest.mock import patch

import pandas as pd

from bot.token_watcher import get_base_data


class TestRunner(unittest.IsolatedAsyncioTestCase):
    @patch("bot.token_watcher.get_time_frame_ohlcv")
    @patch("bot.token_watcher.add_trader_actions_to_dataframe")
    async def test_get_base_data(self, mock_add_trader_actions, mock_get_time_frame):
        # Mock data for add_trader_actions_to_dataframe
        trader_actions_data = pd.DataFrame(
            {
                "trader_1_state": [1, 2, 3],
                "trader_2_state": [0, 1, 0],
            }
        )
        mock_add_trader_actions.return_value = trader_actions_data

        # Mock data for get_time_frame_ohlcv
        ohlcv_data = pd.DataFrame(
            {
                "token": ["SOL", "SOL", "SOL"],
                "trading_minute": pd.date_range("2024-12-01 00:00:00", periods=3, freq="min"),
                "total_volume": [100, 200, 300],
                "price": [10.0, 10.5, 11.0],
            }
        )

        mock_get_time_frame.return_value = ohlcv_data

        # Prepare inputs
        valid_trades = []  # Not used as we mock the function
        trading_minute = datetime(2024, 12, 1, 0, 2)
        token = "SOL"

        # Call the function
        result = await get_base_data(valid_trades, trading_minute, token)

        # Expected result
        expected_result = pd.DataFrame(
            {
                "trader_1_state": [1, 2, 3],
                "trader_2_state": [0, 1, 0],
                "token": ["SOL", "SOL", "SOL"],
                "trading_minute": pd.date_range("2024-12-01 00:00:00", periods=3, freq="min"),
                "total_volume": [100, 200, 300],
                "price": [10.0, 10.5, 11.0],
            }
        )

        # Assert DataFrame equality
        pd.testing.assert_frame_equal(result, expected_result)

        # Verify mocks were called with the correct arguments
        mock_add_trader_actions.assert_called_once_with(valid_trades, trading_minute)
        mock_get_time_frame.assert_called_once_with(token, trading_minute, 11, "1m")


if __name__ == "__main__":
    unittest.main()

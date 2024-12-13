import unittest
from datetime import datetime

import pandas as pd

from data.trade_data import add_trader_actions_to_dataframe
from dto.trade_model import Trade


class TestRunner(unittest.TestCase):
    def setUp(self):
        self.trading_minute = datetime(2024, 11, 30, 15, 45)

        # Sample trades for testing
        self.trades = [
            Trade("trader1", "token", 1, 1, True, 5, datetime(2024, 11, 30, 15, 44).isoformat()),
            Trade("trader1", "token", 1, 1, False, 2, datetime(2024, 11, 30, 15, 43).isoformat()),
            Trade("trader2", "token", 1, 1, True, 3, datetime(2024, 11, 30, 15, 42).isoformat()),
            Trade("trader2", "token", 1, 1, False, 0, datetime(2024, 11, 30, 15, 41).isoformat()),
        ]

    def test_add_trader_actions_to_dataframe(self):
        # Call the function
        df = add_trader_actions_to_dataframe(self.trades, self.trading_minute)

        # Assert DataFrame structure and values
        self.assertIsInstance(df, pd.DataFrame)
        self.assertIn("trader_trader1_state", df.columns)
        self.assertIn("trader_trader2_state", df.columns)

        # Check some specific values
        self.assertEqual(len(df["trader_trader1_state"]), 10)  # 10-minute range
        self.assertEqual(len(df["trader_trader2_state"]), 10)


if __name__ == "__main__":
    unittest.main()

import unittest
from datetime import datetime, timedelta

import pandas as pd

from constants import TRADING_MINUTE_COLUMN
from data.trade_data import create_dataframe_with_trades
from dto.trade_model import Trade


class TestRunner(unittest.TestCase):
    def setUp(self):
        self.trading_minute = datetime(2024, 11, 30, 15, 45)
        self.time_frame = 10

        # Sample trades for testing
        self.trades = [
            Trade("trader1", "token1", 1, 5, True, 5, datetime(2024, 11, 30, 15, 44).isoformat(), ""),
            Trade("trader1", "token1", 1, 10, False, 2, datetime(2024, 11, 30, 15, 43).isoformat(), ""),
            Trade("trader1", "token1", 1, 3, False, 2, datetime(2024, 11, 30, 15, 42).isoformat(), ""),
            Trade("trader2", "token2", 1, 1, True, 3, datetime(2024, 11, 30, 15, 42).isoformat(), ""),
            Trade("trader2", "token2", 1, 1, False, 1, datetime(2024, 11, 30, 15, 41).isoformat(), ""),
        ]

    def test_create_dataframe_with_trades(self):
        # Call the function
        df = create_dataframe_with_trades(self.trades, self.trading_minute, self.time_frame)

        # Assert that the DataFrame is correctly created
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), self.time_frame)  # Ensure correct number of rows

        # Verify columns for traders
        self.assertIn("trader1_sol_amount_spent", df.columns)
        self.assertIn("trader1_sol_amount_received", df.columns)
        self.assertIn("trader2_sol_amount_spent", df.columns)
        self.assertIn("trader2_sol_amount_received", df.columns)

        # Check specific values for a known row
        row = df[df[TRADING_MINUTE_COLUMN] == self.trading_minute - timedelta(minutes=3)].iloc[0]
        self.assertEqual(row["trader1_sol_amount_spent"], 0)
        self.assertEqual(row["trader1_sol_amount_received"], 3)
        self.assertEqual(row["trader2_sol_amount_spent"], 1)
        self.assertEqual(row["trader2_sol_amount_received"], 1)

        row = df[df[TRADING_MINUTE_COLUMN] == self.trading_minute - timedelta(minutes=6)].iloc[0]
        self.assertEqual(row["trader1_sol_amount_spent"], 0)
        self.assertEqual(row["trader1_sol_amount_received"], 0)
        self.assertEqual(row["trader2_sol_amount_spent"], 0)
        self.assertEqual(row["trader2_sol_amount_received"], 0)

        row = df[df[TRADING_MINUTE_COLUMN] == self.trading_minute].iloc[0]
        self.assertEqual(row["trader1_sol_amount_spent"], 5)
        self.assertEqual(row["trader1_sol_amount_received"], 13)
        self.assertEqual(row["trader2_sol_amount_spent"], 1)
        self.assertEqual(row["trader2_sol_amount_received"], 1)


if __name__ == "__main__":
    unittest.main()

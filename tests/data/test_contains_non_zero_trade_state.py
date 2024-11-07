import unittest

import pandas as pd

from data.sliding_window import contains_non_zero_trade_state


class TestRunner(unittest.TestCase):
    def test_no_trade_columns(self):
        # DataFrame without any matching trade columns
        df = pd.DataFrame({
            'other_column': [0, 0, 0],
            'another_column': [0, 0, 0]
        })
        self.assertFalse(contains_non_zero_trade_state(df))

    def test_all_zero_trade_columns(self):
        # DataFrame with trade columns, all values are zero
        df = pd.DataFrame({
            'trade_wallet1_state': [0, 0, 0],
            'trade_wallet2_state': [0, 0, 0]
        })
        self.assertFalse(contains_non_zero_trade_state(df))

    def test_non_zero_in_trade_column(self):
        # DataFrame with a non-zero value in a trade column
        df = pd.DataFrame({
            'trade_wallet1_state': [0, 0, 5],
            'trade_wallet2_state': [0, 0, 0]
        })
        self.assertTrue(contains_non_zero_trade_state(df))

    def test_mixed_columns_with_non_zero_trade_column(self):
        # DataFrame with both trade and other columns, trade column has non-zero value
        df = pd.DataFrame({
            'trade_wallet1_state': [0, 2, 0],
            'other_column': [0, 0, 0]
        })
        self.assertTrue(contains_non_zero_trade_state(df))

    def test_all_zero_trade_and_other_columns(self):
        # DataFrame with trade and other columns, all zero
        df = pd.DataFrame({
            'trade_wallet1_state': [0, 0, 0],
            'trade_wallet2_state': [0, 0, 0],
            'other_column': [0, 0, 0]
        })
        self.assertFalse(contains_non_zero_trade_state(df))


if __name__ == '__main__':
    unittest.main()

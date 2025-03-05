import unittest

import pandas as pd

from constants import TOKEN_COLUMN, TRADING_MINUTE_COLUMN, PRICE_COLUMN
from data.label_data import label_without_time_window


class TestRunner(unittest.TestCase):

    def test_label_without_time_window(self):
        # Create test data
        test_data = pd.DataFrame({
            TOKEN_COLUMN: ['token1'] * 10 + ['token2'] * 10 + ['token3'] * 10,
            TRADING_MINUTE_COLUMN: list(range(10)) + list(range(10)) + list(range(10)),
            PRICE_COLUMN: [100, 102, 104, 106, 110, 108, 107, 105, 103, 101] +  # Prices for token1
                          [200, 250, 300, 1001, 600, 1300, 1300, 1300, 1300, 1300] +  # Prices for token2
                          [2000, 1800, 1600, 1400, 200, 200, 200, 200, 200, 200],  # Prices for token3 (50% decrease)
        })
        actual = label_without_time_window(test_data, 100)
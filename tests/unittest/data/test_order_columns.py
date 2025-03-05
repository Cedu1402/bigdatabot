import unittest
from datetime import datetime

import pandas as pd

from constants import TOKEN_COLUMN, PRICE_COLUMN, TRADING_MINUTE_COLUMN
from data.model_data import order_columns


class TestRunner(unittest.TestCase):

    def test_label_window_positive(self):
        # Arrange
        test_token = "test"
        trading_data = pd.DataFrame([
            [test_token, 1, datetime(2024, 1, 1, 10, 1)],
            [test_token, 1, datetime(2024, 1, 1, 10, 2)],
            [test_token, 1, datetime(2024, 1, 1, 10, 3)],
            [test_token, 3, datetime(2024, 1, 1, 10, 4)],
        ], columns=[TOKEN_COLUMN, PRICE_COLUMN, TRADING_MINUTE_COLUMN])
        expected_order = [PRICE_COLUMN, TOKEN_COLUMN, TRADING_MINUTE_COLUMN]

        # Act
        actual = order_columns([trading_data], expected_order)

        # Assert
        actual_columns = list(actual[0].columns)
        self.assertEqual(expected_order, actual_columns)

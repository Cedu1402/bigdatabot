import unittest
from datetime import datetime

import pandas as pd

from constants import TOKEN_COlUMN, PRICE_COLUMN, TRADING_MINUTE_COLUMN
from data.label_data import label_window


class TestRunner(unittest.TestCase):

    def test_label_window_positive(self):
        # Arrange
        test_token = "test"
        trading_data = pd.DataFrame([
            [test_token, 1, datetime(2024, 1, 1, 10, 1)],
            [test_token, 1, datetime(2024, 1, 1, 10, 2)],
            [test_token, 1, datetime(2024, 1, 1, 10, 3)],
            [test_token, 3, datetime(2024, 1, 1, 10, 4)],
        ], columns=[TOKEN_COlUMN, PRICE_COLUMN, TRADING_MINUTE_COLUMN])

        window_data = trading_data[0:2]

        # Act
        actual = label_window(trading_data, window_data, 100, 50)

        # Assert
        self.assertTrue(actual)

    def test_label_window_negative(self):
        # Arrange
        test_token = "test"
        trading_data = pd.DataFrame([
            [test_token, 5, datetime(2024, 1, 1, 10, 1)],
            [test_token, 4, datetime(2024, 1, 1, 10, 2)],
            [test_token, 4, datetime(2024, 1, 1, 10, 3)],
            [test_token, 1, datetime(2024, 1, 1, 10, 4)],
        ], columns=[TOKEN_COlUMN, PRICE_COLUMN, TRADING_MINUTE_COLUMN])

        window_data = trading_data[0:2]

        # Act
        actual = label_window(trading_data, window_data, 100, 50)

        # Assert
        self.assertFalse(actual)

    def test_label_window_negative_with_bigger_first(self):
        # Arrange
        test_token = "test"
        trading_data = pd.DataFrame([
            [test_token, 4, datetime(2024, 1, 1, 10, 1)],
            [test_token, 1, datetime(2024, 1, 1, 10, 2)],
            [test_token, 1, datetime(2024, 1, 1, 10, 3)],
            [test_token, 1.3, datetime(2024, 1, 1, 10, 4)],
        ], columns=[TOKEN_COlUMN, PRICE_COLUMN, TRADING_MINUTE_COLUMN])

        window_data = trading_data[0:2]

        # Act
        actual = label_window(trading_data, window_data, 100, 50)

        # Assert
        self.assertFalse(actual)


    def test_label_window_negative_neither(self):
        # Arrange
        test_token = "test"
        trading_data = pd.DataFrame([
            [test_token, 1, datetime(2024, 1, 1, 10, 1)],
            [test_token, 1, datetime(2024, 1, 1, 10, 2)],
            [test_token, 1, datetime(2024, 1, 1, 10, 3)],
            [test_token, 1, datetime(2024, 1, 1, 10, 4)],
        ], columns=[TOKEN_COlUMN, PRICE_COLUMN, TRADING_MINUTE_COLUMN])

        window_data = trading_data[0:2]

        # Act
        actual = label_window(trading_data, window_data, 100, 50)

        # Assert
        self.assertFalse(actual)
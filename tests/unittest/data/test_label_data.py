import unittest

import pandas as pd

from constants import TOKEN_COLUMN, TRADING_MINUTE_COLUMN, PRICE_COLUMN, LABEL_COLUMN
from data.label_data import label_dataset


class TestRunner(unittest.TestCase):

    def test_label_dataset(self):
        # Create test data
        test_data = pd.DataFrame({
            TOKEN_COLUMN: ['token1'] * 10 + ['token2'] * 10 + ['token3'] * 10,
            TRADING_MINUTE_COLUMN: list(range(10)) + list(range(10)) + list(range(10)),
            PRICE_COLUMN: [100, 102, 104, 106, 110, 108, 107, 105, 103, 101] +  # Prices for token1
                          [200, 250, 300, 1001, 600, 1300, 1300, 1300, 1300, 1300] +  # Prices for token2
                          [2000, 1800, 1600, 1400, 200, 200, 200, 200, 200, 200],  # Prices for token3 (50% decrease)
        })

        win_percentage = 100  # 50% price increase
        draw_down_percentage = 50  # 100% price decrease
        window_minutes = 5  # Forward-looking window (e.g., 5 trading minutes)

        labeled_data = label_dataset(test_data, win_percentage, draw_down_percentage, window_minutes)
        self.assertIn(LABEL_COLUMN, labeled_data.columns)
        self.assertEqual(len(labeled_data), 5 * 3)
        # Check that all labels for token1 are False
        token1_labels = labeled_data[labeled_data[TOKEN_COLUMN] == 'token1'][LABEL_COLUMN]
        self.assertTrue((token1_labels == False).all())  # Ensure all are False

        # Check that all labels for token2 are True until 1000, then False
        token2_data = labeled_data[labeled_data[TOKEN_COLUMN] == 'token2']
        token2_labels_true = token2_data[token2_data[PRICE_COLUMN] <= 1000][LABEL_COLUMN]
        token2_labels_false = token2_data[token2_data[PRICE_COLUMN] > 1000][LABEL_COLUMN]
        self.assertTrue((token2_labels_true == True).all())  # Ensure all <= 1000 are True
        self.assertTrue((token2_labels_false == False).all())  # Ensure all > 1000 are False

        # Check that all labels for token3 are False
        token3_labels = labeled_data[labeled_data[TOKEN_COLUMN] == 'token3'][LABEL_COLUMN]
        self.assertTrue((token3_labels == False).all())  # Ensure all are False

    def test_label_dataset_dump_before_pump(self):
        # Create test data
        test_data = pd.DataFrame({
            TOKEN_COLUMN: ['token1'] * 10 + ['token2'] * 10,
            TRADING_MINUTE_COLUMN: list(range(10)) + list(range(10)),
            PRICE_COLUMN: [100, 102, 104, 106, 110, 200, 400, 50, 60, 40] +  # Prices for token1
                          [100, 100, 100, 100, 100, 50, 1300, 1300, 1300, 1300]  # Prices for token2
        })

        win_percentage = 100  # 50% price increase
        draw_down_percentage = 50  # 100% price decrease
        window_minutes = 5  # Forward-looking window (e.g., 5 trading minutes)

        labeled_data = label_dataset(test_data, win_percentage, draw_down_percentage, window_minutes)
        self.assertIn(LABEL_COLUMN, labeled_data.columns)
        self.assertEqual(len(labeled_data), 5 * 2)
        # Check that all labels for token1 are False
        token1_labels = labeled_data[labeled_data[TOKEN_COLUMN] == 'token1'][LABEL_COLUMN]
        self.assertTrue((token1_labels == True).all())  # Ensure all are False

        # Check that all labels for token2 are True until 1000, then False
        token2_data = labeled_data[labeled_data[TOKEN_COLUMN] == 'token2'][LABEL_COLUMN]
        self.assertTrue((token2_data == False).all())  # Ensure all are False

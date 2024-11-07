import os
import unittest

from data.feature_engineering import add_features
from data.pickle_files import load_from_pickle, save_to_pickle
from test_constants import TEST_DATA_FOLDER


class TestRunner(unittest.TestCase):

    def test_add_trader_info_to_price_data(self):
        # Arrange
        data = load_from_pickle(os.path.join(TEST_DATA_FOLDER, "combined.pkl"))
        columns = len(data.columns)
        # Act
        actual = add_features(data)
        # Assert
        self.assertEqual(columns + 7, len(actual.columns))
        save_to_pickle(actual, os.path.join(TEST_DATA_FOLDER, "combined_with_features.pkl"))
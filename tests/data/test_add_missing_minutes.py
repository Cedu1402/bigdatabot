import os
import unittest

from data.close_volume_data import add_missing_minutes
from data.pickle_files import load_from_pickle, save_to_pickle
from dune.data_transform import transform_dune_result_to_pandas
from test_constants import TEST_DATA_FOLDER, SAVE_TEST_DATA


class TestRunner(unittest.TestCase):


    def test_add_missing_minutes(self):
        # Arrange
        raw_data = load_from_pickle(os.path.join(TEST_DATA_FOLDER, "4233197.pkl"))
        data = transform_dune_result_to_pandas(raw_data)
        # Act
        actual = add_missing_minutes(data.copy())
        # Assert
        self.assertGreater(len(actual), len(data))
        # Assert: Check that each token has exactly 240 minutes of data
        for token in actual['token'].unique():
            token_data = actual[actual['token'] == token]
            self.assertEqual(len(token_data), 240, f"Token {token} does not have 4 hours (240 minutes) of data.")

        if SAVE_TEST_DATA:
            save_to_pickle(actual, os.path.join(TEST_DATA_FOLDER, "complete_close_volume.pkl"))
import os
import unittest

from data.close_volume_data import add_missing_minutes
from data.pickle_files import load_from_pickle
from dune.data_transform import transform_dune_result_to_pandas
from test_constants import TEST_DATA_FOLDER


class TestRunner(unittest.TestCase):


    def test_add_missing_minutes(self):
        # Arrange
        raw_data = load_from_pickle(os.path.join(TEST_DATA_FOLDER, "4233197.pkl"))
        data = transform_dune_result_to_pandas(raw_data)
        # Act
        actual = add_missing_minutes(data.copy())
        # Assert
        self.assertGreater(len(actual), len(data))
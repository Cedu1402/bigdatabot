import os
import unittest

from data.label_data import label_data
from data.pickle_files import load_from_pickle
from test_constants import TEST_DATA_FOLDER


class TestRunner(unittest.TestCase):

    def test_label_data(self):
        # Arrange
        volume_data = load_from_pickle(os.path.join(TEST_DATA_FOLDER, "complete_close_volume.pkl"))
        sliding_window_data = load_from_pickle(os.path.join(TEST_DATA_FOLDER, "sliding_windows.pkl"))

        # Act
        actual = label_data(sliding_window_data, volume_data)

        # Assert

import os
import unittest


from data.pickle_files import load_from_pickle, save_to_pickle
from data.sliding_window import create_sliding_windows
from test_constants import TEST_DATA_FOLDER


class TestRunner(unittest.TestCase):

    def test_create_sliding_windows(self):
        # Arrange
        data = load_from_pickle(os.path.join(TEST_DATA_FOLDER, "combined.pkl"))
        amount_tokens = len(data['token'].unique())
        # Act
        sliding_window_data = create_sliding_windows(data)
        # Assert
        self.assertEqual(amount_tokens * 231, len(sliding_window_data))
        save_to_pickle(sliding_window_data, os.path.join(TEST_DATA_FOLDER, "sliding_window.pkl"))
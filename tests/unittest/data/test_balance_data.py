import unittest

import pandas as pd

from constants import LABEL_COLUMN
from data.data_split import balance_data


class TestRunner(unittest.TestCase):

    def setUp(self):
        # Create mock data with True and False labels
        self.true_data = [pd.DataFrame({LABEL_COLUMN: [True]}) for _ in range(10)]
        self.false_data = [pd.DataFrame({LABEL_COLUMN: [False]}) for _ in range(5)]
        self.data = self.true_data + self.false_data

    def test_balanced_output(self):
        """Test that balance_data returns an equal number of True and False labeled DataFrames."""
        result = balance_data(self.data)

        # Check if result has an equal number of True and False labels
        true_count = sum(1 for item in result if item[LABEL_COLUMN].iloc[0])
        false_count = sum(1 for item in result if not item[LABEL_COLUMN].iloc[0])

        self.assertEqual(true_count, false_count, "The output is not balanced between True and False labels.")

    def test_output_size(self):
        """Test that the output size is twice the minimum number of True or False labeled DataFrames in the input."""
        result = balance_data(self.data)
        min_count = min(len(self.true_data), len(self.false_data))

        # Expect twice the min count (as we want balanced True/False DataFrames)
        self.assertEqual(len(result), 2 * min_count, "The output size does not match the expected balanced size.")

    def test_no_modification_of_original_data(self):
        """Test that the original data list remains unchanged."""
        original_data_copy = self.data.copy()
        balance_data(self.data)
        self.assertEqual(self.data, original_data_copy, "The original data was modified by balance_data.")

    def test_empty_input(self):
        """Test that an empty input list returns an empty output list."""
        result = balance_data([])
        self.assertEqual(result, [], "Empty input should return an empty output.")

    def test_single_class_input(self):
        """Test that input with only one class returns a balanced subset (all items of the single class)."""
        single_class_data = [pd.DataFrame({LABEL_COLUMN: [True]}) for _ in range(10)]
        result = balance_data(single_class_data)

        # Since there are no False items, result should only contain True items.
        self.assertTrue(all(item[LABEL_COLUMN].iloc[0] for item in result), "Result should contain only True items.")


if __name__ == '__main__':
    unittest.main()

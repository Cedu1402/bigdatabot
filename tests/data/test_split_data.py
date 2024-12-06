import unittest
from typing import List

import pandas as pd

from data.data_split import split_data


class TestSplitData(unittest.TestCase):

    def setUp(self):
        # Create sample data
        self.data: List[pd.DataFrame] = [
            pd.DataFrame({'col1': [i], 'col2': [i + 1]}) for i in range(100)
        ]
        self.train_ratio = 0.7
        self.val_ratio = 0.15
        self.test_ratio = 0.15

    def test_split_ratios_sum_to_one(self):
        # Test if function raises ValueError when ratios do not sum to 1
        with self.assertRaises(ValueError):
            split_data(self.data, train_ratio=0.6, val_ratio=0.3, test_ratio=0.2)

    def test_output_lengths(self):
        # Test if data is split into expected lengths
        train_data, val_data, test_data = split_data(
            self.data, train_ratio=self.train_ratio, val_ratio=self.val_ratio, test_ratio=self.test_ratio
        )
        total_samples = len(self.data)

        expected_train_len = int(total_samples * self.train_ratio)
        expected_val_len = int(total_samples * self.val_ratio)
        expected_test_len = total_samples - expected_train_len - expected_val_len

        self.assertEqual(len(train_data), expected_train_len)
        self.assertEqual(len(val_data), expected_val_len)
        self.assertEqual(len(test_data), expected_test_len)

    def test_all_data_included(self):
        # Test if all data points are included in the split (no data lost)
        train_data, val_data, test_data = split_data(
            self.data, train_ratio=self.train_ratio, val_ratio=self.val_ratio, test_ratio=self.test_ratio
        )
        split_data_set = set(map(id, train_data + val_data + test_data))
        original_data_set = set(map(id, self.data))

        self.assertEqual(split_data_set, original_data_set)

    def test_no_data_overlap(self):
        # Test if there's no overlap between train, validation, and test sets
        train_data, val_data, test_data = split_data(
            self.data, train_ratio=self.train_ratio, val_ratio=self.val_ratio, test_ratio=self.test_ratio
        )

        # Convert lists to sets of object IDs to check for overlap
        train_set = set(map(id, train_data))
        val_set = set(map(id, val_data))
        test_set = set(map(id, test_data))

        self.assertTrue(train_set.isdisjoint(val_set))
        self.assertTrue(train_set.isdisjoint(test_set))
        self.assertTrue(val_set.isdisjoint(test_set))


if __name__ == '__main__':
    unittest.main()


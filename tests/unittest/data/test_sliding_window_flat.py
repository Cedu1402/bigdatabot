import unittest

import pandas as pd

from data.sliding_window import create_sliding_window_flat


class TestRunner(unittest.TestCase):
    def setUp(self):
        # Sample data for testing
        self.data = pd.DataFrame({
            'token': ['A', 'A', 'A', 'B', 'B', 'B', 'C', 'C'],
            'value': [10, 20, 30, 5, 15, 25, 40, 50]
        })
        self.token_column = 'token'
        self.expected_step_1 = self.data  # Step size 1 should return the original DataFrame
        self.expected_step_2 = pd.DataFrame({
            'token': ['A', 'A', 'B', 'B', 'C'],
            'value': [10, 30, 5, 25, 40]
        })

    def test_step_size_1(self):
        # Test with step size 1
        result = create_sliding_window_flat(self.data, step_size=1)
        pd.testing.assert_frame_equal(result, self.expected_step_1)

    def test_step_size_2(self):
        # Test with step size 2
        result = create_sliding_window_flat(self.data, step_size=2)
        pd.testing.assert_frame_equal(result, self.expected_step_2)

    def test_empty_dataframe(self):
        # Test with an empty DataFrame
        empty_df = pd.DataFrame(columns=self.data.columns)
        result = create_sliding_window_flat(empty_df, step_size=2)
        self.assertTrue(result.empty)

    def test_invalid_step_size(self):
        # Test with invalid step size (e.g., zero or negative)
        with self.assertRaises(ValueError):
            create_sliding_window_flat(self.data, step_size=0)
        with self.assertRaises(ValueError):
            create_sliding_window_flat(self.data, step_size=-1)


if __name__ == '__main__':
    unittest.main()

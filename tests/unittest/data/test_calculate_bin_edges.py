import unittest

import pandas as pd

from data.feature_engineering import compute_bin_edges


class TestRunner(unittest.TestCase):

    def setUp(self):
        # Sample DataFrame for testing
        self.data = pd.DataFrame({
            'A': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            'B': [10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
            'C': [5, 3, 6, 9, 1, 2, 8, 7, 4, 10]
        })

    def test_bin_edges_computation(self):
        # Specify columns and number of bins
        columns = ['A', 'B']
        n_bins = 4

        # Compute bin edges
        bin_edges = compute_bin_edges(self.data, columns, n_bins)

        # Verify that bin edges are computed for each specified column
        self.assertIn('A', bin_edges)
        self.assertIn('B', bin_edges)

        # Check if bin edges are correct length (n_bins + 1)
        self.assertEqual(len(bin_edges['A']), n_bins + 1)
        self.assertEqual(len(bin_edges['B']), n_bins + 1)

        # Verify that the returned bin edges are sorted and unique
        self.assertTrue(all(bin_edges['A'][i] < bin_edges['A'][i + 1] for i in range(len(bin_edges['A']) - 1)))
        self.assertTrue(all(bin_edges['B'][i] < bin_edges['B'][i + 1] for i in range(len(bin_edges['B']) - 1)))

    def test_missing_column(self):
        # Test when a non-existent column is specified
        columns = ['A', 'D']  # 'D' is not in the DataFrame
        n_bins = 4

        # Compute bin edges
        bin_edges = compute_bin_edges(self.data, columns, n_bins)

        # Verify that only existing columns are included in the result
        self.assertIn('A', bin_edges)
        self.assertNotIn('D', bin_edges)

    def test_invalid_n_bins(self):
        # Test with a number of bins larger than unique values in a column
        columns = ['C']
        n_bins = 15  # More bins than unique values

        # Compute bin edges
        bin_edges = compute_bin_edges(self.data, columns, n_bins)

        # Verify that bin edges for 'C' are still returned and duplicates are dropped
        self.assertIn('C', bin_edges)
        self.assertTrue(len(bin_edges['C']) <= n_bins + 1)  # Adjusted for duplicates='drop'


if __name__ == '__main__':
    unittest.main()

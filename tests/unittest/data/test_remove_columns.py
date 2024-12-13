import unittest

import pandas as pd

from data.model_data import remove_columns


class TestRunner(unittest.TestCase):

    def setUp(self):
        # Sample data for testing
        self.data = [
            pd.DataFrame({
                'A': [1, 2, 3],
                'B': [4, 5, 6],
                'C': [7, 8, 9]
            }),
            pd.DataFrame({
                'A': [10, 11, 12],
                'B': [13, 14, 15],
                'C': [16, 17, 18]
            })
        ]

    def test_remove_existing_columns(self):
        # Remove columns that exist in the data
        columns_to_remove = ['B', 'C']
        result = remove_columns(self.data, columns_to_remove)

        # Check that columns are removed
        for df in result:
            self.assertNotIn('B', df.columns)
            self.assertNotIn('C', df.columns)
            self.assertIn('A', df.columns)  # 'A' should remain

    def test_remove_nonexistent_column(self):
        # Remove a column that doesn't exist
        columns_to_remove = ['D']  # Column 'D' doesn't exist
        result = remove_columns(self.data, columns_to_remove)

        # Check that no columns were removed and no error occurred
        for df in result:
            self.assertIn('A', df.columns)
            self.assertIn('B', df.columns)
            self.assertIn('C', df.columns)

    def test_remove_mixed_columns(self):
        # Remove a mix of existing and non-existing columns
        columns_to_remove = ['A', 'D']  # 'A' exists, 'D' doesn't
        result = remove_columns(self.data, columns_to_remove)

        # Check that 'A' was removed but 'D' had no effect
        for df in result:
            self.assertNotIn('A', df.columns)
            self.assertIn('B', df.columns)
            self.assertIn('C', df.columns)


if __name__ == '__main__':
    unittest.main()

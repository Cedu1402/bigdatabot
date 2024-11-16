import unittest

import pandas as pd

from data.label_data import get_min_max_with_indices


class TestRunner(unittest.TestCase):

    def test_get_min_max_with_indices(self):
        # Example DataFrame
        df = pd.DataFrame({
            'value': [10, 20, 15, 30, 25, 40, 35, 50]
        })

        x = 3  # Number of rows to look ahead

        # Apply the function to the 'value' column
        df = get_min_max_with_indices(df['value'], x)

        # Drop NaN values
        df_dropped = df.dropna()

        # Check that the length of the DataFrame after dropping NaN is 5
        self.assertEqual(len(df_dropped), 5)

        # Check that min/max values and their corresponding indices are correct
        self.assertEqual(df['min_value'].iloc[0], 15.0)
        self.assertEqual(df['min_index'].iloc[0], 2)
        self.assertEqual(df['max_value'].iloc[0], 30.0)
        self.assertEqual(df['max_index'].iloc[0], 3)

        self.assertEqual(df['min_value'].iloc[1], 15.0)
        self.assertEqual(df['min_index'].iloc[1], 2)
        self.assertEqual(df['max_value'].iloc[1], 30.0)
        self.assertEqual(df['max_index'].iloc[1], 3)

        self.assertEqual(df['min_value'].iloc[3], 25.0)
        self.assertEqual(df['min_index'].iloc[3], 4)
        self.assertEqual(df['max_value'].iloc[3], 40.0)
        self.assertEqual(df['max_index'].iloc[3], 5)


if __name__ == '__main__':
    unittest.main()

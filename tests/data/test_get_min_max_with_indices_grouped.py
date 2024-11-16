import unittest
import pandas as pd

from constants import TOKEN_COlUMN, PRICE_COLUMN
from data.label_data import get_min_max_with_indices_grouped


class TestRunner(unittest.TestCase):

    def test_get_min_max_with_indices_grouped(self):
        # Example DataFrame with token grouping
        df = pd.DataFrame({
            TOKEN_COlUMN: ['A', 'A', 'A', 'B', 'B', 'B'],
            PRICE_COLUMN: [10, 20, 15, 30, 25, 40]
        })

        x = 2  # Number of rows to look ahead
        token_column = 'token'

        # Apply the grouped function
        df['min_value'], df['min_index'], df['max_value'], df['max_index'] = get_min_max_with_indices_grouped(df, x,
                                                                                                              token_column)

        # Drop NaN values
        df_dropped = df.dropna()

        # Check that the length of the DataFrame after dropping NaN is correct
        self.assertEqual(len(df_dropped), 2)

        # Check values for group 'A'
        self.assertEqual(df['min_value'].iloc[0], 15.0)
        self.assertEqual(df['min_index'].iloc[0], 2)
        self.assertEqual(df['max_value'].iloc[0], 20.0)
        self.assertEqual(df['max_index'].iloc[0], 1)

        # Check values for group 'B'
        self.assertEqual(df['min_value'].iloc[3], 25.0)
        self.assertEqual(df['min_index'].iloc[3], 4)
        self.assertEqual(df['max_value'].iloc[3], 40.0)
        self.assertEqual(df['max_index'].iloc[3], 5)


if __name__ == '__main__':
    unittest.main()

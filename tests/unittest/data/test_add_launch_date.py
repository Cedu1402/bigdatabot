import unittest

import pandas as pd

from constants import TOKEN_COLUMN, LAUNCH_DATE_COLUMN
from data.feature_engineering import add_launch_date


class TestRunner(unittest.TestCase):

    def test_add_launch_date(self):
        # Arrange
        df2 = pd.DataFrame({
            TOKEN_COLUMN: ['token_a', 'token_b', 'token_d'],
            'value': [100, 200, 300]
        })

        # Create sample data for df1 (this would be the data with launch_date)
        df1 = pd.DataFrame({
            TOKEN_COLUMN: ['token_a', 'token_b', 'token_b', 'token_d'],
            LAUNCH_DATE_COLUMN: ['2022-01-01', '2022-02-01', '2022-02-01', '2022-03-01']
        })

        # Act
        data = add_launch_date(df1, df2)

        # Assert
        self.assertEqual(data.shape[0], df2.shape[0])
        self.assertEqual(data.shape[1], df2.shape[1] + 1)

import unittest

import pandas as pd

from constants import TOKEN_COlUMN, TOTAL_VOLUME_COLUMN, TRADING_MINUTE_COLUMN, CUMULATIVE_VOLUME
from data.feature_engineering import add_cumulative_volume


class TestRunner(unittest.TestCase):

    def test_add_cumulative_volume(self):
        # Arrange
        data = pd.DataFrame({
            TOKEN_COlUMN: ['token1', 'token1', 'token1', 'token2', 'token2', 'token2'],
            TOTAL_VOLUME_COLUMN: [10, 20, 30, 40, 50, 60],
            TRADING_MINUTE_COLUMN: [1, 2, 3, 1, 2, 3]  # This is the timestep
        })

        # Act
        data = add_cumulative_volume(data)

        # Assert
        self.assertEqual(4, data.shape[1])
        self.assertEqual(10, data[CUMULATIVE_VOLUME].iloc[0])
        self.assertEqual(30, data[CUMULATIVE_VOLUME].iloc[1])
        self.assertEqual(60, data[CUMULATIVE_VOLUME].iloc[2])
        self.assertEqual(40, data[CUMULATIVE_VOLUME].iloc[3])
        self.assertEqual(90, data[CUMULATIVE_VOLUME].iloc[4])
        self.assertEqual(150, data[CUMULATIVE_VOLUME].iloc[5])

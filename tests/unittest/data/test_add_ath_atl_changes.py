import unittest

import pandas as pd

from constants import TOKEN_COLUMN, TRADING_MINUTE_COLUMN, PRICE_COLUMN, CHANGE_FROM_ATH, CHANGE_FROM_ATL
from data.feature_engineering import add_ath_atl_changes


class TestRunner(unittest.TestCase):

    def test_add_ath_atl_changes(self):
        # Arrange
        data = pd.DataFrame({
            TOKEN_COLUMN: ['token1', 'token1', 'token1', 'token2', 'token2', 'token2'],
            PRICE_COLUMN: [10, 15, 8, 20, 25, 18],  # Current price for each row
            TRADING_MINUTE_COLUMN: [1, 2, 3, 1, 2, 3]
        })

        # Act
        data = add_ath_atl_changes(data)

        # Assert
        self.assertEqual(5, data.shape[1])
        self.assertAlmostEqual(data.loc[0, CHANGE_FROM_ATL], 0.0, places=2)
        self.assertAlmostEqual(data.loc[1, CHANGE_FROM_ATL], 50.0, places=2)
        self.assertAlmostEqual(data.loc[2, CHANGE_FROM_ATL], 0.0, places=2)
        self.assertAlmostEqual(data.loc[0, CHANGE_FROM_ATH], 0.0, places=2)
        self.assertAlmostEqual(data.loc[1, CHANGE_FROM_ATH], 0, places=2)
        self.assertAlmostEqual(data.loc[2, CHANGE_FROM_ATH], -46.67, places=2)

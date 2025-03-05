import unittest

import pandas as pd

from constants import TOKEN_COLUMN, TRADING_MINUTE_COLUMN, PRICE_COLUMN
from data.data_split import get_index_of_similar_price


class TestFindClosestTrade(unittest.TestCase):
    def setUp(self):
        """Set up sample test data"""
        self.data = pd.DataFrame({
            TOKEN_COLUMN: ["A", "A", "A", "B", "B", "B"],
            PRICE_COLUMN: [100, 200, 310, 150, 250, 350],
            'age': [100, 200, 310, 150, 250, 350]
        })
        self.current_price = 220  # Test with a given price level

    def test_find_closest_trade(self):
        """Test if the function returns the correct closest trading minute index"""
        result = get_index_of_similar_price(self.data, self.current_price)

        expected = {
            "A": 1,  # Closest to 220 is 200 (index 1)
            "B": 4  # Closest to 220 is 250 (index 1)
        }

        self.assertIsInstance(result, pd.Series, "Output should be a Pandas Series")
        self.assertEqual(result.to_dict(), expected, f"Expected {expected}, but got {result.to_dict()}")


# Run the tests
if __name__ == "__main__":
    unittest.main()

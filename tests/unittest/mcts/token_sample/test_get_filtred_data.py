import unittest

import pandas as pd

from constants import TOKEN_COLUMN
from mcts.token_sample import get_filtered_data


class TestGetFilteredData(unittest.TestCase):

    def setUp(self):
        # Sample DataFrame for testing
        self.data = pd.DataFrame({
            TOKEN_COLUMN: ['BTC', 'ETH', 'BTC', 'SOL', 'ETH'],
            'price': [30000, 2000, 31000, 50, 2100],
            'volume': [100, 200, 150, 300, 250]
        })

    def test_get_filtered_data(self):
        # Select specific tokens to filter
        selected_tokens = ['BTC', 'SOL']
        result = get_filtered_data(self.data, selected_tokens)

        # Expected DataFrame
        expected = pd.DataFrame({
            TOKEN_COLUMN: ['BTC', 'BTC', 'SOL'],
            'price': [30000, 31000, 50],
            'volume': [100, 150, 300]
        }).reset_index(drop=True)

        # Check if the result matches the expected DataFrame
        pd.testing.assert_frame_equal(result, expected)


if __name__ == '__main__':
    unittest.main()

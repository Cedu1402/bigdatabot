import unittest

import pandas as pd

from constants import TOKEN_COlUMN
from mcts.token_sample import split_by_token


class TestRunner(unittest.TestCase):

    def setUp(self):
        # Sample test DataFrame
        self.data = pd.DataFrame({
            TOKEN_COlUMN: ['BTC', 'ETH', 'BTC', 'SOL', 'ETH'],
            'price': [30000, 2000, 31000, 50, 2100],
        })

    def test_split_by_token(self):
        # Run function
        result = split_by_token(self.data)

        # Assert keys are correct
        self.assertCountEqual(result.keys(), ['BTC', 'ETH', 'SOL'])

        # Check the DataFrame content for one token
        pd.testing.assert_frame_equal(
            result['BTC'],
            pd.DataFrame({
                TOKEN_COlUMN: ['BTC', 'BTC'],
                'price': [30000, 31000],
            }).reset_index(drop=True)
        )


if __name__ == '__main__':
    unittest.main()

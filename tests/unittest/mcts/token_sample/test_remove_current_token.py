import unittest

import pandas as pd

from constants import TOKEN_COlUMN
from mcts.token_sample import remove_current_token


class TestRunner(unittest.TestCase):

    def setUp(self):
        # Sample test DataFrame
        self.data = pd.DataFrame({
            TOKEN_COlUMN: ['BTC', 'ETH', 'BTC', 'SOL', 'ETH'],
            'price': [30000, 2000, 31000, 50, 2100],
        })

    def test_remove_current_token(self):
        # Run function
        result = remove_current_token(self.data, 'BTC')
        # Check the DataFrame content for one token
        pd.testing.assert_frame_equal(
            result,
            pd.DataFrame({
                TOKEN_COlUMN: ['ETH', 'SOL', 'ETH'],
                'price': [2000, 50, 2100],
            })
        )


if __name__ == '__main__':
    unittest.main()

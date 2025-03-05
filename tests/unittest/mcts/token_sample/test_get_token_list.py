import unittest

import pandas as pd

from constants import TOKEN_COLUMN
from mcts.token_sample import get_token_list


class TestRunner(unittest.TestCase):

    def setUp(self):
        # Sample test DataFrame
        self.data = pd.DataFrame({
            TOKEN_COLUMN: ['BTC', 'ETH', 'BTC', 'SOL', 'ETH'],
            'price': [30000, 2000, 31000, 50, 2100],
        })

    def test_get_token_list(self):
        # Run function
        result = get_token_list(self.data)
        # Check the DataFrame content for one token
        self.assertCountEqual(["BTC", 'ETH', 'SOL'], result)


if __name__ == '__main__':
    unittest.main()

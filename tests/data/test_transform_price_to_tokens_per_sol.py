import unittest

import pandas as pd

from constants import PRICE_COLUMN
from data.data_format import transform_price_to_tokens_per_sol


class TestRunner(unittest.TestCase):
    def test_transform_price_to_tokens_per_sol(self):
        # Input test data
        data = pd.DataFrame({
            PRICE_COLUMN: [10.0, 20.0, 40.0],
            "token": ["TokenA", "TokenB", "TokenC"]
        })
        solana_price = 100.0

        # Expected output
        expected_data = pd.DataFrame({
            PRICE_COLUMN: [10.0, 5.0, 2.5],  # 100 / 10, 100 / 20, 100 / 40
            "token": ["TokenA", "TokenB", "TokenC"]
        })

        # Call the function
        result = transform_price_to_tokens_per_sol(data.copy(), solana_price)

        # Assert the output
        pd.testing.assert_frame_equal(result, expected_data)

if __name__ == "__main__":
    unittest.main()

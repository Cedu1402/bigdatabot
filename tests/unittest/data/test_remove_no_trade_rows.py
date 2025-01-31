import unittest

import pandas as pd

from data.combine_price_trades import remove_no_trade_rows


class TestRunner(unittest.TestCase):
    def setUp(self):
        # Sample input DataFrame
        self.data = pd.DataFrame({
            'trading_minute': [1, 2, 3, 4, 5, 6],
            'token': ['A', 'A', 'A', 'B', 'B', 'C'],
            'A_sol_amount_spent': [0, 10, 0, 0, 0, 0],
            'A_sol_amount_received': [0, 0, 0, 0, 0, 0],
            'B_sol_amount_spent': [0, 0, 0, 5, 0, 0],
            'B_sol_amount_received': [0, 0, 0, 0, 0, 0],
            'C_sol_amount_spent': [0, 0, 0, 0, 0, 0],
            'C_sol_amount_received': [0, 0, 0, 0, 0, 0]
        })

        # Expected output after filtering
        self.expected_data = pd.DataFrame({
            'trading_minute': [2, 3, 4, 5],
            'token': ['A', 'A', 'B', 'B'],
            'A_sol_amount_spent': [10, 0, 0, 0],
            'A_sol_amount_received': [0, 0, 0, 0],
            'B_sol_amount_spent': [0, 0, 5, 0],
            'B_sol_amount_received': [0, 0, 0, 0],
            'C_sol_amount_spent': [0, 0, 0, 0],
            'C_sol_amount_received': [0, 0, 0, 0]
        }).reset_index(drop=True)

    def test_remove_no_trade_rows(self):
        # Call the function
        result = remove_no_trade_rows(self.data)

        # Compare the result with the expected output
        pd.testing.assert_frame_equal(result.reset_index(drop=True), self.expected_data)


if __name__ == '__main__':
    unittest.main()

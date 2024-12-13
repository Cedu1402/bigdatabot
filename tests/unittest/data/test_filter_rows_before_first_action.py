import unittest

import pandas as pd
from pandas.testing import assert_frame_equal

from constants import TOKEN_COlUMN, TRADING_MINUTE_COLUMN
from data.combine_price_trades import TraderState, filter_rows_before_first_action


class TestRunner(unittest.TestCase):

    def setUp(self):
        # Sample data to test the function
        self.data = pd.DataFrame({
            TOKEN_COlUMN: ['token1', 'token1', 'token1', 'token2', 'token2'],
            TRADING_MINUTE_COLUMN: pd.to_datetime(['2024-11-17 00:00', '2024-11-17 00:01', '2024-11-17 00:02',
                                                   '2024-11-17 00:00', '2024-11-17 00:01']),
            'trader_1_state': [TraderState.NO_ACTION, TraderState.JUST_BOUGHT, TraderState.STILL_HOLDS,
                               TraderState.STILL_HOLDS, TraderState.JUST_SOLD],
            'trader_2_state': [TraderState.NO_ACTION, TraderState.NO_ACTION, TraderState.NO_ACTION,
                               TraderState.JUST_BOUGHT, TraderState.STILL_HOLDS]
        })

    def test_filter_rows_before_first_action(self):
        # Apply the filter function
        filtered_result = filter_rows_before_first_action(self.data)

        # Expected output based on the given logic:
        expected_data = pd.DataFrame({
            TOKEN_COlUMN: ['token1', 'token1', 'token2', 'token2'],
            TRADING_MINUTE_COLUMN: pd.to_datetime(['2024-11-17 00:01', '2024-11-17 00:02',
                                                   '2024-11-17 00:00', '2024-11-17 00:01']),
            'trader_1_state': [TraderState.JUST_BOUGHT, TraderState.STILL_HOLDS, TraderState.STILL_HOLDS,
                               TraderState.JUST_SOLD],
            'trader_2_state': [TraderState.NO_ACTION, TraderState.NO_ACTION, TraderState.JUST_BOUGHT,
                               TraderState.STILL_HOLDS]
        })

        filtered_result_reset = filtered_result.reset_index(drop=True)
        expected_data_reset = expected_data.reset_index(drop=True)


        # Assert that the filtered result matches the expected output
        assert_frame_equal(expected_data_reset, filtered_result_reset)


if __name__ == '__main__':
    unittest.main()

import os
import unittest

from data.close_volume_data import add_missing_minutes
from data.combine_price_trades import add_trader_info_to_price_data
from data.pickle_files import load_from_pickle, save_to_pickle
from data.sliding_window import contains_non_zero_trade_state
from data.solana_trader import get_trader_from_trades
from dune.data_transform import transform_dune_result_to_pandas
from test_constants import TEST_DATA_FOLDER


class TestRunner(unittest.TestCase):

    def test_add_trader_info_to_price_data(self):
        # Arrange
        price_data = load_from_pickle(os.path.join(TEST_DATA_FOLDER, "complete_close_volume.pkl"))
        raw_data = load_from_pickle(os.path.join(TEST_DATA_FOLDER, "4229277.pkl"))
        trades_data = transform_dune_result_to_pandas(raw_data)
        trader = get_trader_from_trades(trades_data)
        expected = price_data.copy()
        # Act
        actual = add_trader_info_to_price_data(price_data, trader, trades_data)
        # Assert
        self.assertEqual(len(expected.columns) + 50, len(actual.columns))
        self.assertEqual(len(expected), len(actual))
        self.assertTrue(contains_non_zero_trade_state(actual))
        save_to_pickle(actual, os.path.join(TEST_DATA_FOLDER, "combined.pkl"))

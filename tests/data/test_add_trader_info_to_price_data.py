import os
import unittest

from data.close_volume_data import add_missing_minutes
from data.combine_price_trades import add_trader_info_to_price_data
from data.pickle_files import load_from_pickle, save_to_pickle
from data.solana_trader import get_trader_from_trades
from dune.data_transform import transform_dune_result_to_pandas
from test_constants import TEST_DATA_FOLDER


class TestRunner(unittest.TestCase):

    def test_add_trader_info_to_price_data(self):
        # Arrange
        raw_data = load_from_pickle(os.path.join(TEST_DATA_FOLDER, "4233197.pkl"))
        volume_data = transform_dune_result_to_pandas(raw_data)
        volume_data = add_missing_minutes(volume_data)
        raw_data = load_from_pickle(os.path.join(TEST_DATA_FOLDER, "4229277.pkl"))
        trades_data = transform_dune_result_to_pandas(raw_data)
        trader = get_trader_from_trades(trades_data)
        # Act
        actual = add_trader_info_to_price_data(volume_data, trader, trades_data)
        save_to_pickle(actual, '../test_data/combined.pkl')
        # Assert
        self.assertEqual(len(volume_data.columns) + 100, len(actual.columns))
        self.assertEqual(len(volume_data), len(actual))
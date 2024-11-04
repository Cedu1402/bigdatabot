import os
import unittest

from data.pickle_files import load_from_pickle
from data.solana_trader import get_trader_from_trades
from dune.data_transform import transform_dune_result_to_pandas
from test_constants import TEST_DATA_FOLDER


class TestRunner(unittest.TestCase):

    def test_get_trader_from_trades(self):
        # Arrange
        raw_data = load_from_pickle(os.path.join(TEST_DATA_FOLDER, "4229277.pkl"))
        data = transform_dune_result_to_pandas(raw_data)
        # Act
        actual = get_trader_from_trades(data)
        # Assert
        self.assertEqual(50, len(actual))

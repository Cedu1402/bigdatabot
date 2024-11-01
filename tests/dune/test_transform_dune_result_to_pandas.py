import unittest
from unittest.mock import patch

from cache_helper import get_cache_data
from constants import DUNE_API_KEY, TRADE_LIST_QUERY
from dune.data_transform import transform_dune_result_to_pandas


class TestRunner(unittest.TestCase):

    @patch.dict("os.environ", {DUNE_API_KEY: "fake_key"})
    def test_get_trader_list_env_loaded(self):
        # Arrange
        raw_data = get_cache_data(TRADE_LIST_QUERY)
        # Act
        actual = transform_dune_result_to_pandas(raw_data)
        # Assert
        self.assertEqual(len(actual), 1476)

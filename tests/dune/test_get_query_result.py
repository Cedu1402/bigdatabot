import unittest
from unittest.mock import patch

from constants import DUNE_API_KEY, TRADE_LIST_QUERY
from dune.query_request import get_query_result


class TestRunner(unittest.TestCase):

    @patch.dict("os.environ", {DUNE_API_KEY: "fake_key"})
    def test_get_trader_list_env_loaded(self):
        # Arrange
        # Act
        actual = get_query_result(TRADE_LIST_QUERY)
        # Assert
        self.assertEqual(len(actual), 1476)

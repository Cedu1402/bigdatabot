import unittest

import pandas as pd
from dotenv import load_dotenv

from constants import PRODUCTION_TEST_TRADES
from dune.query_request import get_query_result_with_params


class TestRunner(unittest.TestCase):

    def test_get_query_result_with_params(self):
        # Arrange
        load_dotenv()

        # Act
        actual = get_query_result_with_params(PRODUCTION_TEST_TRADES,
                                              {"min_token_age_h": 2,
                                               "token": "GPtAcyTawh8YrmA2XzyjssBpfuTNHhyerBoeXTG9pump"}, True)
        # Assert
        self.assertIsNotNone(actual)
        self.assertEqual(type(actual), pd.DataFrame)

import unittest

from dotenv import load_dotenv

from constants import PRODUCTION_TEST_TRADES
from dune.query_request import get_from_api_with_params


class TestRunner(unittest.TestCase):

    def test_get_from_api_with_params(self):
        # Arrange
        load_dotenv()

        # Act
        actual = get_from_api_with_params(PRODUCTION_TEST_TRADES,
                                          {"min_token_age_h": 2,
                                           "token": "GPtAcyTawh8YrmA2XzyjssBpfuTNHhyerBoeXTG9pump"})
        # Assert
        self.assertIsNotNone(actual)

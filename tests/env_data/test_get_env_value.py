import unittest
from unittest.mock import patch

from constants import DUNE_API_KEY
from env_data.get_env_value import get_env_value


class TestRunner(unittest.TestCase):

    @patch.dict("os.environ", {DUNE_API_KEY: "fake_key"})
    def test_get_api_key_env_loaded(self):
        # Arrange
        expected = "fake_key"
        # Act
        actual = get_env_value(DUNE_API_KEY)
        # Assert
        self.assertEqual(expected, actual)

    @patch.dict("os.environ", {}, clear=True)
    def test_get_api_key_env_not_loaded(self):
        # Arrange
        expected = None
        # Act
        actual = get_env_value(DUNE_API_KEY)
        # Assert
        self.assertEqual(expected, actual)

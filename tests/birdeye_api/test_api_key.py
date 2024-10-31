import unittest
from unittest.mock import patch

from birdeye_api.api_key import get_api_key


class TestRunner(unittest.TestCase):

    @patch.dict("os.environ", {"BIRDEYE_KEY": "fake_key"})
    def test_get_api_key_env_loaded(self):
        # Arrange
        expected = "fake_key"
        # Act
        actual = get_api_key()
        # Assert
        self.assertEqual(expected, actual)

    @patch.dict("os.environ", {}, clear=True)
    def test_get_api_key_env_not_loaded(self):
        # Arrange
        expected = None
        # Act
        actual = get_api_key()
        # Assert
        self.assertEqual(expected, actual)

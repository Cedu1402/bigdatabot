import unittest
from unittest.mock import patch

from dune_client.client import DuneClient

from constants import DUNE_API_KEY
from dune.dune_client import get_dune_client
from env_data.get_env_value import get_env_value


class TestRunner(unittest.TestCase):

    @patch.dict("os.environ", {DUNE_API_KEY: "fake_key"})
    def test_get_dune_client_env_loaded(self):
        # Arrange
        # Act
        actual = get_dune_client()
        # Assert
        self.assertEqual(DuneClient, type(actual))

    @patch.dict("os.environ", {}, clear=True)
    def test_get_dune_client_env_not_loaded(self):
        # Arrange
        # Act
        actual = get_dune_client()
        # Assert
        self.assertEqual(None, actual)

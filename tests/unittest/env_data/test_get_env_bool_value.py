import unittest
from unittest.mock import patch

from constants import DUNE_API_KEY
from env_data.get_env_value import get_env_bool_value


class TestRunner(unittest.TestCase):

    @patch.dict("os.environ", {DUNE_API_KEY: "false"})
    def test_get_env_bool_value_false(self):
        # Act
        actual = get_env_bool_value(DUNE_API_KEY)
        # Assert
        self.assertFalse(actual)

    @patch.dict("os.environ", {DUNE_API_KEY: "true"})
    def test_get_env_bool_value_true(self):
        # Act
        actual = get_env_bool_value(DUNE_API_KEY)
        # Assert
        self.assertTrue(actual)

    @patch.dict("os.environ", {}, clear=True)
    def test_get_api_key_env_not_loaded(self):
        # Act
        actual = get_env_bool_value(DUNE_API_KEY)
        # Assert
        self.assertFalse(actual)

import unittest
from datetime import datetime

from dotenv import load_dotenv

from birdeye_api.token_creation_endpoint import get_token_create_info
from constants import PUMP_DOT_FUN_AUTHORITY


class TestRunner(unittest.IsolatedAsyncioTestCase):

    async def test_get_token_create_time(self):
        # Arrange
        load_dotenv()
        token = "HHNmZNnCZ5jNxDCobBtLmvtj5JnJb2LWBNntXsBmpump"
        expected_date = datetime.strptime("2024-11-28 08:34:57", "%Y-%m-%d %H:%M:%S")
        # Act
        date, owner = await get_token_create_info(token)
        # Assert
        self.assertEqual(expected_date, date)
        self.assertEqual(owner, PUMP_DOT_FUN_AUTHORITY)

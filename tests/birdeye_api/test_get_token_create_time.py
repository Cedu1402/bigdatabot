import unittest
from datetime import datetime

from dotenv import load_dotenv
from solana.rpc.async_api import AsyncClient

from birdeye_api.token_creation_endpoint import get_token_create_time


class TestRunner(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.client = AsyncClient("https://api.mainnet-beta.solana.com")

    async def asyncTearDown(self):
        await self.client.close()

    async def test_get_token_create_time(self):
        # Arrange
        load_dotenv()
        token = "HHNmZNnCZ5jNxDCobBtLmvtj5JnJb2LWBNntXsBmpump"
        expected_date = datetime.strptime("2024-11-28 08:34:57", "%Y-%m-%d %H:%M:%S")
        # Act
        date = await get_token_create_time(token)
        # Assert
        self.assertEqual(expected_date, date)

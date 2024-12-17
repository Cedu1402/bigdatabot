import unittest

from solana.rpc.async_api import AsyncClient
from solders.pubkey import Pubkey

from solana_api.solana_data import get_recent_signature


class TestRunner(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.client = AsyncClient("https://api.mainnet-beta.solana.com")

    async def asyncTearDown(self):
        await self.client.close()

    async def test_get_recent_signature(self):
        # Arrange
        user = Pubkey.from_string("B5QzGuMknM2jTwUPzTBL4SbV6Zta6VAGMpTADCkbiwAq")
        # Act
        latest_tx = await get_recent_signature(self.client, user)

        # Assert
        self.assertIsNotNone(latest_tx)

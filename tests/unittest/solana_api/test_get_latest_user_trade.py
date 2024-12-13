import unittest

from solders.pubkey import Pubkey

from solana_api.solana_data import get_latest_user_trade


class TestRunner(unittest.IsolatedAsyncioTestCase):

    async def test_get_sol_change(self):
        # Arrange
        user = Pubkey.from_string("FRXA6YDW1Ufu6TQRbaySAQLtkbTLHqtLaAQkhHmJY9eS")
        # Act
        latest_tx = await get_latest_user_trade(user, "https://api.mainnet-beta.solana.com")

        # Assert
        self.assertIsNotNone(latest_tx)

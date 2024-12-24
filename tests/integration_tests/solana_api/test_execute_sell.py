import os
import unittest

from dotenv import load_dotenv
from solana.rpc.async_api import AsyncClient

from constants import SOL_RPC
from solana_api.trader import setup_buy, execute_sell


class TestRunner(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        load_dotenv()
        self.client = AsyncClient(os.getenv(SOL_RPC, "https://api.mainnet-beta.solana.com"))

    async def asyncTearDown(self):
        await self.client.close()

    async def test_execute_buy_usdc(self):
        # Arrange
        sol_client, wallet, _ = setup_buy()
        token = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"  # The token to swap to

        # Act
        actual = await execute_sell(token, 10000, sol_client, wallet)

        # Assert
        self.assertTrue(actual, "Failed to sell tokens.")


if __name__ == "__main__":
    unittest.main()

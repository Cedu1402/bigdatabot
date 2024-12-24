import os
import unittest
from datetime import datetime

from dotenv import load_dotenv
from solana.rpc.async_api import AsyncClient

from constants import SOL_RPC
from solana_api.trader import setup_buy, execute_buy


class TestRunner(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        load_dotenv()
        self.client = AsyncClient(os.getenv(SOL_RPC, "https://api.mainnet-beta.solana.com"))

    async def asyncTearDown(self):
        await self.client.close()

    async def test_execute_buy_usdc(self):
        # Arrange
        sol_client, wallet, r = setup_buy()
        token = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"  # The token to swap to
        sol_to_invest = 1 / 250  # $1 in SOL (adjust based on real-time SOL price)
        max_retry_time = 60  # Maximum retry time in seconds
        max_higher_price = 5  # Maximum allowed percentage increase

        # Simulate initial conditions
        start_time = datetime.now()
        start_price_api = 100  # Simulated API price in USD
        current_sol_price = 20.0  # Replace with real SOL price if available

        # Act
        amount_bought, start_price = await execute_buy(
            start_time=start_time,
            max_retry_time=max_retry_time,
            token=token,
            sol_to_invest=sol_to_invest,
            start_price_api=start_price_api,
            sol_client=sol_client,
            wallet=wallet,
            current_sol_price=current_sol_price,
            max_higher_price=max_higher_price,
            start_price=None
        )

        # Assert
        self.assertIsNotNone(amount_bought, "Failed to buy tokens.")
        self.assertGreater(amount_bought, 0, "No tokens were bought.")


if __name__ == "__main__":
    unittest.main()

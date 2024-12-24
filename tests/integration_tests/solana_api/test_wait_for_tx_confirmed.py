import unittest

from solana.rpc.async_api import AsyncClient

from solana_api.trader import wait_for_tx_confirmed


class TestRunner(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.client = AsyncClient("https://api.mainnet-beta.solana.com")

    async def asyncTearDown(self):
        await self.client.close()

    async def test_wait_for_tx_confirmed(self):
        # Arrange
        tx = "5XZS91aJU9YfK98NEM3LzehEcsi4Vbd56Ti58XsThUFBq7nTVUvSKCgskGUMSXPyAGthzendCreVkZyf1bnHSJr1"

        # Act
        confirmed = await wait_for_tx_confirmed(self.client, tx, 10)

        # Assert
        self.assertTrue(confirmed)

    async def test_wait_for_tx_confirmed_failed(self):
        # Arrange
        tx = "2ERpp2DqgDhmjC3AZG36i7LJNk9FG8vuJoTcAUyQH7B8TQH7WQvq59QzSsuxBV6vX1HEpwQ9J3wLQDQfndCUJeYM"

        # Act
        confirmed = await wait_for_tx_confirmed(self.client, tx, 10)

        # Assert
        self.assertFalse(confirmed)

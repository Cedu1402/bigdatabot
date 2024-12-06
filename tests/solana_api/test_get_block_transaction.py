import unittest

from solana.rpc.async_api import AsyncClient

from solana_api.solana_data import get_block_transactions


class TestRunner(unittest.IsolatedAsyncioTestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = AsyncClient("https://api.mainnet-beta.solana.com")

    @classmethod
    async def tearDownClass(cls):
        await cls.client.close()

    async def test_get_block_transactions(self):
        # Arrange
        slot = 303641496

        # Act
        transactions = await get_block_transactions(self.client, slot)

        # Assert
        self.assertIsInstance(transactions, list)
        for tx in transactions[:1]:
            self.assertTrue(hasattr(tx, "transaction"), "Missing 'transaction' attribute")
            self.assertTrue(hasattr(tx, "meta"), "Missing 'meta' attribute")
            self.assertIsNotNone(tx.transaction, "Transaction data is None")
            self.assertIsNotNone(tx.meta, "Meta data is None")

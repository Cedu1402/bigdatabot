import unittest

from solana.rpc.async_api import AsyncClient
from solders.signature import Signature

from solana_api.solana_data import is_raydium_trade, transform_to_encoded_transaction_with_status_meta


class TestRunner(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.client = AsyncClient("https://api.mainnet-beta.solana.com")

    async def asyncTearDown(self):
        await self.client.close()

    async def test_is_raydium_trade_buy(self):
        # Arrange
        signature = "5BgxKpS2r888Vo736rGnCFewu1uv8bpKqqiXGtQE8GSEtk6m6iD8pDVmSSeXvVwgvAZTNvJpcYHZSuz8wHuETQGB"
        tx_response = await self.client.get_transaction(Signature.from_string(signature), max_supported_transaction_version=0)
        tx = transform_to_encoded_transaction_with_status_meta(tx_response)

        # Act
        is_trade = is_raydium_trade(tx)

        # Assert
        self.assertTrue(is_trade)

    async def test_is_raydium_trade_no(self):
        # Arrange
        signature = "Jx3Zbpg78dz1LyKtHjD9qvVM2UxenWu827iPUmZKL76N8G6MrQrQQtS4upzhpn7QsG7itvz9WDDHeGn8yrBqZ6g"
        tx_response = await self.client.get_transaction(Signature.from_string(signature), max_supported_transaction_version=0)
        tx = transform_to_encoded_transaction_with_status_meta(tx_response)

        # Act
        is_trade = is_raydium_trade(tx)

        # Assert
        self.assertFalse(is_trade)
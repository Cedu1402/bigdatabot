import unittest

from solana.rpc.async_api import AsyncClient
from solders.pubkey import Pubkey
from solders.signature import Signature

from solana_api.solana_data import transform_to_encoded_transaction_with_status_meta, get_token_change


class TestRunner(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.client = AsyncClient("https://api.mainnet-beta.solana.com")

    async def asyncTearDown(self):
        await self.client.close()

    async def test_get_token_change_simple(self):
        # Arrange
        signature = "2qDbG76HcBNo5dzKkUaLar9xrefXDfzswV5bcrkxB4sBthmiKQR6mtzoPfhk9TWYyKsNZwriktAsSaQ975G1sc9N"
        tx_response = await self.client.get_transaction(Signature.from_string(signature),
                                                        max_supported_transaction_version=0)

        tx = transform_to_encoded_transaction_with_status_meta(tx_response)
        user = Pubkey.from_string("J3aATskv2GHRYvYu1C6HsLF26joxPyBFDvU4dDvV7RDv")
        # Act
        token, change, holding = get_token_change(tx, user)

        # Assert
        self.assertEqual("AAMN63PjTHM75vDgjbhcYtywdsGnw5aUHcpRRL3Mpump", token)
        self.assertEqual(1787794.448831, change)
        self.assertEqual(1787794.448831, holding)

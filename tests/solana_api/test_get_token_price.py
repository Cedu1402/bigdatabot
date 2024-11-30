import unittest

from solana_api.jupiter_api import get_token_price


class TestRunner(unittest.IsolatedAsyncioTestCase):


    async def test_get_token_price(self):
        token = "7Sra5CkgY8MYwfVKtXDfFLon57W78WBFWTUTDQHNpump"

        actual = await get_token_price(token)

        self.assertGreater(actual, 0)
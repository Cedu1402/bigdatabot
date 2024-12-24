import unittest

from solana_api.jupiter_api import get_quote


class TestRunner(unittest.IsolatedAsyncioTestCase):

    async def test_get_recent_signature(self):
        # Act
        quote = await get_quote("8UgqoFQgqFPfdMiAXLvBqJhVBgcYCxntry6easSJpump",
                                1 * (10 ** 9), True)

        # Assert
        self.assertIsNotNone(quote)

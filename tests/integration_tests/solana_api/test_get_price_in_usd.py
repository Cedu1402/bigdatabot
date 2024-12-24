import unittest

from solana_api.jupiter_api import get_quote
from solana_api.trader import get_price_in_usd


class TestRunner(unittest.IsolatedAsyncioTestCase):

    async def test_get_recent_signature(self):
        # Arrange
        sol_amount = 1
        sol_amount_raw = sol_amount * (10 ** 9)
        quote = await get_quote("8UgqoFQgqFPfdMiAXLvBqJhVBgcYCxntry6easSJpump",
                                sol_amount_raw, True)

        # Act
        price = get_price_in_usd(quote, sol_amount, 150)

        # Assert
        self.assertIsNotNone(price)

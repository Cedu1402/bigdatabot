import unittest

from solana_api.jupiter_api import get_quote, get_price_in_usd_sell, get_price_in_usd_buy


class TestRunner(unittest.IsolatedAsyncioTestCase):

    async def test_get_recent_signature(self):
        # Arrange
        sol_amount = 1
        sol_amount_raw = sol_amount * (10 ** 9)
        quote = await get_quote("8UgqoFQgqFPfdMiAXLvBqJhVBgcYCxntry6easSJpump",
                                sol_amount_raw, True)

        # Act
        price = get_price_in_usd_buy(quote, sol_amount, 150)

        # Assert
        self.assertIsNotNone(price)

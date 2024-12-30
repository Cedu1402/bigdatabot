import unittest

from solana_api.jupiter_api import get_quote, get_price_in_usd_sell, get_price_in_usd_buy


class TestRunner(unittest.IsolatedAsyncioTestCase):

    async def test_get_price_in_usd_buy(self):
        # Arrange
        sol_amount = 1
        sol_amount_raw = sol_amount * (10 ** 9)
        quote = await get_quote("8FwucaJUNtw9fQmpbmT7HSXMm8mKAi3sLnUSKaq4pump",
                                sol_amount_raw, True)

        # Act
        price = get_price_in_usd_buy(quote, sol_amount, 193)

        # Assert
        self.assertIsNotNone(price)

    async def test_get_price_in_usd_sell(self):
        # Arrange
        token_amount = 500000
        token_amount_raw = token_amount * (10 ** 6)
        quote = await get_quote("8FwucaJUNtw9fQmpbmT7HSXMm8mKAi3sLnUSKaq4pump",
                                token_amount_raw, False)

        # Act
        price = get_price_in_usd_sell(quote, token_amount, 193)

        # Assert
        self.assertIsNotNone(price)

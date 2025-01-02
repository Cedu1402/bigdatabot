import unittest

from solana_api.jupiter_api import get_quote, get_price_in_usd_sell, get_price_in_usd_buy


class TestRunner(unittest.IsolatedAsyncioTestCase):

    async def test_get_price_in_usd_buy(self):
        # Arrange
        sol_amount = 0.2631578947368421
        sol_amount_raw = int(sol_amount * (10 ** 9))
        quote = await get_quote("9UTQN4PXGdpe9jd61the92M93nh3f5jUBq5kQiJypump",
                                sol_amount_raw, True)

        # Act
        price = get_price_in_usd_buy(quote, sol_amount_raw, 193)

        # Assert
        self.assertIsNotNone(price)

    async def test_get_price_in_usd_sell(self):
        # Arrange
        token_amount = 500000
        token_amount_raw = token_amount * (10 ** 6)
        quote = await get_quote("9UTQN4PXGdpe9jd61the92M93nh3f5jUBq5kQiJypump",
                                token_amount_raw, False)

        # Act
        price = get_price_in_usd_sell(quote, token_amount_raw, 193)

        # Assert
        self.assertIsNotNone(price)

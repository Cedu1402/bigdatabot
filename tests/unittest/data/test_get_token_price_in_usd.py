import unittest

from data.feature_engineering import get_token_price_in_usd


# Assuming the function get_token_price_in_usd is in a module called `your_module`
# from your_module import get_token_price_in_usd


class TestRunner(unittest.TestCase):

    def test_standard_case(self):
        tokens_per_sol = 2  # 2 tokens per SOL
        sol_price_usd = 10  # Price of 1 SOL is $10
        expected_price = 5
        self.assertEqual(get_token_price_in_usd(tokens_per_sol, sol_price_usd), expected_price)

    def test_zero_sol_price(self):
        tokens_per_sol = 10  # 10 tokens per SOL
        sol_price_usd = 0  # Price of 1 SOL is $0
        expected_price = 0  # 10 tokens per SOL * 0 USD per SOL = 0 USD per token
        self.assertEqual(get_token_price_in_usd(tokens_per_sol, sol_price_usd), expected_price)

    def test_zero_tokens_per_sol(self):
        tokens_per_sol = 0  # 0 tokens per SOL
        sol_price_usd = 10  # Price of 1 SOL is $10
        expected_price = 0  # 0 tokens per SOL * 10 USD per SOL = 0 USD per token
        self.assertEqual(get_token_price_in_usd(tokens_per_sol, sol_price_usd), expected_price)


if __name__ == "__main__":
    unittest.main()

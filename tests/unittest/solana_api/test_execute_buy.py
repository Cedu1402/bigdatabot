import unittest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch, MagicMock

from solana_api.trader import execute_buy


class TestRunner(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.start_time = datetime.now()
        self.max_retry_time = 60
        self.token = "SOL"
        self.sol_to_invest = 1
        self.start_price_api = 100
        self.current_sol_price = 20.0
        self.max_higher_price = 10
        self.wallet = MagicMock()  # Mock Keypair
        self.sol_client = AsyncMock()  # Mock AsyncClient
        self.start_price = None

    @patch("solana_api.trader.get_quote", new_callable=AsyncMock)
    @patch("solana_api.trader.get_price_in_usd")
    @patch("solana_api.trader.swap_from_quote", new_callable=AsyncMock)
    @patch("solana_api.trader.wait_for_tx_confirmed", new_callable=AsyncMock)
    @patch("solana_api.trader.get_token_balance", new_callable=AsyncMock)
    async def test_buy_success(
            self, mock_get_token_balance, mock_wait_for_tx_confirmed, mock_swap_from_quote, mock_get_price_in_usd,
            mock_get_quote
    ):
        mock_get_quote.return_value = {"quote": "response"}
        mock_get_price_in_usd.side_effect = [100, 100]  # No price change
        mock_swap_from_quote.return_value = "tx_id"
        mock_wait_for_tx_confirmed.return_value = True
        mock_get_token_balance.return_value = 10

        result = await execute_buy(
            self.start_time,
            self.max_retry_time,
            self.token,
            self.sol_to_invest,
            self.start_price_api,
            self.sol_client,
            self.wallet,
            self.current_sol_price,
            self.max_higher_price,
            self.start_price,
        )
        self.assertEqual(result, (10, 100))

    @patch("solana_api.trader.get_quote", new_callable=AsyncMock)
    async def test_retry_time_exceeded(self, mock_get_quote):
        result = await execute_buy(
            self.start_time - timedelta(seconds=61),
            self.max_retry_time,
            self.token,
            self.sol_to_invest,
            self.start_price_api,
            self.sol_client,
            self.wallet,
            self.current_sol_price,
            self.max_higher_price,
            self.start_price,
        )
        self.assertEqual(result, (-1, None))

    @patch("solana_api.trader.get_quote", new_callable=AsyncMock)
    async def test_failed_quote_fetch(self, mock_get_quote):
        mock_get_quote.return_value = None

        result = await execute_buy(
            self.start_time,
            self.max_retry_time,
            self.token,
            self.sol_to_invest,
            self.start_price_api,
            self.sol_client,
            self.wallet,
            self.current_sol_price,
            self.max_higher_price,
            self.start_price,
        )
        self.assertEqual(result, (None, self.start_price_api))

    @patch("solana_api.trader.get_quote", new_callable=AsyncMock)
    @patch("solana_api.trader.get_price_in_usd")
    async def test_price_above_limit(self, mock_get_price_in_usd, mock_get_quote):
        mock_get_quote.return_value = {"quote": "response"}
        mock_get_price_in_usd.side_effect = [100, 111]  # 11% price increase

        result = await execute_buy(
            self.start_time,
            self.max_retry_time,
            self.token,
            self.sol_to_invest,
            self.start_price_api,
            self.sol_client,
            self.wallet,
            self.current_sol_price,
            self.max_higher_price,
            self.start_price,
        )
        self.assertEqual(result, (-1, 100))

    @patch("solana_api.trader.get_quote", new_callable=AsyncMock)
    @patch("solana_api.trader.get_price_in_usd")
    @patch("solana_api.trader.swap_from_quote", new_callable=AsyncMock)
    async def test_failed_transaction(self, mock_swap_from_quote, mock_get_price_in_usd, mock_get_quote):
        mock_get_quote.return_value = {"quote": "response"}
        mock_get_price_in_usd.side_effect = [100, 100]  # No price change
        mock_swap_from_quote.return_value = None  # Transaction fails

        result = await execute_buy(
            self.start_time,
            self.max_retry_time,
            self.token,
            self.sol_to_invest,
            self.start_price_api,
            self.sol_client,
            self.wallet,
            self.current_sol_price,
            self.max_higher_price,
            self.start_price,
        )
        self.assertEqual(result, (None, 100))

    @patch("solana_api.trader.get_quote", new_callable=AsyncMock)
    @patch("solana_api.trader.get_price_in_usd")
    @patch("solana_api.trader.swap_from_quote", new_callable=AsyncMock)
    @patch("solana_api.trader.wait_for_tx_confirmed", new_callable=AsyncMock)
    async def test_transaction_not_confirmed(
            self, mock_wait_for_tx_confirmed, mock_swap_from_quote, mock_get_price_in_usd, mock_get_quote
    ):
        mock_get_quote.return_value = {"quote": "response"}
        mock_get_price_in_usd.side_effect = [100, 100]  # No price change
        mock_swap_from_quote.return_value = "tx_id"
        mock_wait_for_tx_confirmed.return_value = False  # Transaction not confirmed

        result = await execute_buy(
            self.start_time,
            self.max_retry_time,
            self.token,
            self.sol_to_invest,
            self.start_price_api,
            self.sol_client,
            self.wallet,
            self.current_sol_price,
            self.max_higher_price,
            self.start_price,
        )
        self.assertEqual(result, (None, 100))

    @patch("solana_api.trader.get_quote", new_callable=AsyncMock)
    @patch("solana_api.trader.get_price_in_usd")
    @patch("solana_api.trader.swap_from_quote", new_callable=AsyncMock)
    @patch("solana_api.trader.wait_for_tx_confirmed", new_callable=AsyncMock)
    @patch("solana_api.trader.get_token_balance", new_callable=AsyncMock)
    async def test_no_balance_after_buy(
            self, mock_get_token_balance, mock_wait_for_tx_confirmed, mock_swap_from_quote, mock_get_price_in_usd,
            mock_get_quote
    ):
        mock_get_quote.return_value = {"quote": "response"}
        mock_get_price_in_usd.side_effect = [100, 100]  # No price change
        mock_swap_from_quote.return_value = "tx_id"
        mock_wait_for_tx_confirmed.return_value = True
        mock_get_token_balance.return_value = 0  # No balance found

        result = await execute_buy(
            self.start_time,
            self.max_retry_time,
            self.token,
            self.sol_to_invest,
            self.start_price_api,
            self.sol_client,
            self.wallet,
            self.current_sol_price,
            self.max_higher_price,
            self.start_price,
        )
        self.assertEqual(result, (-1, 100))


if __name__ == "__main__":
    unittest.main()

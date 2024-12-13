from datetime import datetime

from database.trade_table import get_trades_by_token, insert_trade
from dto.trade_model import Trade
from tests.integration_tests.database.base_testdb import BaseTestDatabase


class TestRunner(BaseTestDatabase):

    def test_get_trades_by_token(self):
        # Arrange
        token = "test_token"
        trader = "test_trader"
        token_amount = 100
        sol_amount = 50
        buy = True
        token_holding_after = 150
        trade_time = datetime.now()
        tx_signature = "test_signature"

        # Create a Trade object and insert it for testing
        trade = Trade(trader, token, token_amount, sol_amount, buy, token_holding_after, trade_time.isoformat(),
                      tx_signature)
        insert_trade(trade)

        # Act: Get all trades for the given token
        trades = get_trades_by_token(token)

        # Assert: Verify that the correct trades are retrieved
        self.assertGreater(len(trades), 0, "There should be at least one trade for the token")
        self.assertEqual(trades[0].token, token, "The token should match the inserted value")
        self.assertEqual(trades[0].trader, trader, "The trader should match the inserted value")
        self.assertEqual(trades[0].token_amount, token_amount, "The token amount should match the inserted value")
        self.assertEqual(trades[0].sol_amount, sol_amount, "The SOL amount should match the inserted value")
        self.assertEqual(trades[0].buy, buy, "The buy flag should match the inserted value")
        self.assertEqual(trades[0].token_holding_after, token_holding_after,
                         "The token holding after should match the inserted value")
        self.assertEqual(trades[0].trade_time, trade_time.isoformat(),
                         "The trade time should match the inserted value")
        self.assertEqual(trades[0].tx_signature, tx_signature,
                         "The transaction signature should match the inserted value")

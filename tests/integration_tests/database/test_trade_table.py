from datetime import datetime

from database.trade_table import insert_trade
from dto.trade_model import Trade
from tests.integration_tests.database.base_testdb import BaseTestDatabase


class TestRunner(BaseTestDatabase):
    def test_insert_trade(self):
        # Arrange
        trade = Trade(
            trader="test_trader",
            token="test_token",
            token_amount=9323487819740892,
            sol_amount=2433487819740892,
            buy=True,
            token_holding_after=1433487819740892,
            trade_time=datetime.now().isoformat(),
            tx_signature="test_signature"
        )

        # Act
        insert_trade(trade)

        # Assert
        self.cursor.execute("""
            SELECT trader, token, token_amount, sol_amount, buy, token_holding_after, trade_time, tx_signature
            FROM trades
        """)
        result = self.cursor.fetchone()

        self.assertIsNotNone(result, "The trade should be inserted into the database")
        self.assertEqual(result[0], trade.trader, "The trader should match the inserted value")
        self.assertEqual(result[1], trade.token, "The token should match the inserted value")
        self.assertEqual(result[2], trade.token_amount,
                         msg="The token amount should match the inserted value")
        self.assertEqual(result[3], trade.sol_amount,
                         msg="The SOL amount should match the inserted value")
        self.assertEqual(result[4], trade.buy, "The buy flag should match the inserted value")
        self.assertEqual(result[5], trade.token_holding_after,
                         msg="The token holding should match the inserted value")
        self.assertEqual(result[6].isoformat(), trade.get_time().isoformat(),
                         "The trade time should match the inserted value")
        self.assertEqual(result[7], trade.tx_signature,
                         "The trade tx signature should match the inserted value")

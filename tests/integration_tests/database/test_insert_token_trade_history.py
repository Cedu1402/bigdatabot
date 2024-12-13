from datetime import datetime, timedelta

from database.token_trade_history_table import insert_token_trade_history
from dto.token_trade_history_model import TokenTradeHistory
from tests.integration_tests.database.base_testdb import BaseTestDatabase


class TestRunner(BaseTestDatabase):

    def test_insert_token_trade_history(self):
        # Arrange
        token = "test_token"
        buy_time = datetime.now()
        sell_time = buy_time + timedelta(minutes=10)
        buy_price = 10.5
        sell_price = 12.0

        token_trade_history = TokenTradeHistory(
            token=token,
            buy_time=buy_time,
            sell_time=sell_time,
            buy_price=buy_price,
            sell_price=sell_price
        )

        # Act
        insert_token_trade_history(token_trade_history)

        # Assert
        self.cursor.execute("""
            SELECT token, buy_time, sell_time, buy_price, sell_price
            FROM token_trade_history
        """)
        result = self.cursor.fetchone()

        self.assertIsNotNone(result, "The token trade history should be inserted into the database")
        self.assertEqual(result[0], token, "The token should match the inserted value")
        self.assertEqual(result[1].isoformat(), buy_time.isoformat(), "The buy time should match the inserted value")
        self.assertEqual(result[2].isoformat(), sell_time.isoformat(), "The sell time should match the inserted value")
        self.assertEqual(result[3], buy_price, "The buy price should match the inserted value")
        self.assertEqual(result[4], sell_price, "The sell price should match the inserted value")

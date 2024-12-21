from datetime import datetime, timedelta

from database.token_trade_history_table import insert_token_trade_history, update_sell_price
from dto.token_trade_history_model import TokenTradeHistory
from tests.integration_tests.database.base_testdb import BaseTestDatabase


class TestRunner(BaseTestDatabase):

    def test_update_sell_price(self):
        # Arrange
        token = "test_token"
        buy_time = datetime.now()
        sell_time = buy_time + timedelta(minutes=10)
        buy_price = 10.5
        sell_price = 12.0
        new_sell_price = 15.0

        token_trade_history = TokenTradeHistory(
            token=token,
            buy_time=buy_time,
            sell_time=sell_time,
            buy_price=buy_price,
            sell_price=sell_price
        )

        # Insert initial data
        insert_token_trade_history(token_trade_history)

        # Act
        update_sell_price(token, new_sell_price)

        # Assert
        self.cursor.execute("""
            SELECT token, buy_time, sell_time, buy_price, sell_price
            FROM token_trade_history
            WHERE token = %s
        """, (token,))
        result = self.cursor.fetchone()

        self.assertIsNotNone(result, "The token trade history should exist in the database")
        self.assertEqual(result[0], token, "The token should match the inserted value")
        self.assertEqual(result[1].isoformat(), buy_time.isoformat(), "The buy time should match the inserted value")
        self.assertEqual(result[2].isoformat(), sell_time.isoformat(), "The sell time should match the inserted value")
        self.assertEqual(result[3], buy_price, "The buy price should match the inserted value")
        self.assertEqual(result[4], new_sell_price, "The sell price should match the updated value")

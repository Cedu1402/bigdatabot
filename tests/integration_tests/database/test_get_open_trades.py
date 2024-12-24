from datetime import datetime, timedelta
from unittest import TestCase

from database.token_trade_history_table import insert_token_trade_history, get_open_trades
from dto.token_trade_history_model import TokenTradeHistory
from tests.integration_tests.database.base_testdb import BaseTestDatabase


class TestGetOpenTrades(BaseTestDatabase, TestCase):

    def test_get_open_trades(self):
        # Arrange: Insert sample token trade history data
        token_trade_history_1 = TokenTradeHistory(
            token="test_token_1",
            buy_time=datetime.now(),  # Within the valid range
            sell_time=None,  # Open trade
            buy_price=100.0,
            sell_price=None
        )
        token_trade_history_2 = TokenTradeHistory(
            token="test_token_2",
            buy_time=datetime.now() - timedelta(days=3),  # Before the cutoff
            sell_time=None,  # Open trade
            buy_price=150.0,
            sell_price=None
        )
        token_trade_history_3 = TokenTradeHistory(
            token="test_token_3",
            buy_time=datetime.now() - timedelta(days=1),  # Within the valid range
            sell_time=datetime.now(),  # Closed trade
            buy_price=200.0,
            sell_price=250.0
        )

        insert_token_trade_history(token_trade_history_1)
        insert_token_trade_history(token_trade_history_2)
        insert_token_trade_history(token_trade_history_3)

        # Act: Retrieve the count of open trades
        open_trades = get_open_trades()

        # Assert: Verify only open trades after the cutoff are counted
        self.assertEqual(open_trades, 1, "There should be exactly 1 open trade after the cutoff date")

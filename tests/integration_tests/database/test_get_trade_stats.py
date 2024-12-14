from datetime import datetime, timedelta

from database.token_trade_history_table import insert_token_trade_history, get_trade_stats
from dto.token_trade_history_model import TokenTradeHistory
from tests.integration_tests.database.base_testdb import BaseTestDatabase


class TestRunner(BaseTestDatabase):

    def test_get_trade_stats(self):
        # Arrange
        buy_time = datetime.now()
        sell_time = buy_time + timedelta(hours=2)

        # Create dummy trade data using the insert function
        insert_token_trade_history(TokenTradeHistory(
            token="BTC",
            buy_time=buy_time,
            sell_time=sell_time,
            buy_price=10000.00,
            sell_price=11000.00
        ))
        insert_token_trade_history(TokenTradeHistory(
            token="ETH",
            buy_time=buy_time,
            sell_time=sell_time,
            buy_price=2000.00,
            sell_price=1000.00
        ))

        # Act
        stats = get_trade_stats()

        # Assert
        self.assertEqual(stats["total_trades"], 2, "The total trades should match the number of inserted rows.")
        self.assertAlmostEqual(
            stats["total_return"],
            -20,
            places=2,
            msg="The total percentage return should match the calculated value (5%)."
        )

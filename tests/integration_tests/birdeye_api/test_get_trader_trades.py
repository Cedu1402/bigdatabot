import unittest
from datetime import datetime

from dotenv import load_dotenv

from birdeye_api.trades_endpoint import get_trader_trades


class TestRunner(unittest.IsolatedAsyncioTestCase):

    async def test_get_trader_trades(self):
        # Arrange
        load_dotenv()
        token = "9FW3pZkdJwN6z4ePo6wHqd1Eav7Qqy9VaH8uzDMuDUuv"
        start_date = datetime(2024, 12, 30)
        end_date = datetime(2024, 12, 31)

        # Act
        actual = await get_trader_trades(token, start_date, end_date)

        # Assert
        self.assertGreater(len(actual), 0)


if __name__ == '__main__':
    unittest.main()

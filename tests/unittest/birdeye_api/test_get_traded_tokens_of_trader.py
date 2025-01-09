import unittest
from datetime import datetime
from unittest.mock import patch, AsyncMock

from birdeye_api.trades_endpoint import get_traded_tokens_of_trader


class TestRunner(unittest.IsolatedAsyncioTestCase):
    @patch('birdeye_api.trades_endpoint.get_trader_trades', new_callable=AsyncMock)
    async def test_get_traded_tokens_of_trader(self, mock_get_trader_trades):
        test_data = [
            {
                "quote": {
                    "symbol": "USDC",
                    "decimals": 6,
                    "address": "test_1",
                    "amount": 350351441,
                    "type": "transfer",
                    "type_swap": "from",
                    "ui_amount": 350.351441,
                    "price": None,
                    "nearest_price": 0.99991594,
                    "change_amount": -350351441,
                    "ui_change_amount": -350.351441
                },
                "base": {
                    "symbol": "SOL",
                    "decimals": 9,
                    "address": "So11111111111111111111111111111111111111112",
                    "amount": 1610859019,
                    "type": "transfer",
                    "type_swap": "to",
                    "fee_info": None,
                    "ui_amount": 1.610859019,
                    "price": None,
                    "nearest_price": 216.65610374576917,
                    "change_amount": 1610859019,
                    "ui_change_amount": 1.610859019
                },
                "base_price": None,
                "quote_price": None,
                "tx_hash": "3bHiF6b9xmuAjanyLgvKbM2fnFSBo9FeY4rb67xrnGZWx24S6Yyroc8upiJgyUnG29p39jQqxfeRtZ5pTcT9hQJm",
                "source": "lifinity",
                "block_unix_time": 1731555934,
                "tx_type": "swap",
                "address": "DrRd8gYMJu9XGxLhwTCPdHNLXCKHsxJtMpbn62YqmwQe",
                "owner": "GKQBjCn68cTFwUcUiszSioE3B2tAeemfgS2x4Zk2Lyz9"
            },
            {
                "quote": {
                    "symbol": "SHEGEN",
                    "decimals": 6,
                    "address": "test_1",
                    "amount": 7623505077,
                    "type": "transfer",
                    "type_swap": "from",
                    "ui_amount": 7623.505077,
                    "price": 0.026750926577956923,
                    "nearest_price": 0.026890095180012584,
                    "change_amount": -7623505077,
                    "ui_change_amount": -7623.505077
                },
                "base": {
                    "symbol": "SOL",
                    "decimals": 9,
                    "address": "test_2",
                    "amount": 947868014,
                    "type": "transfer",
                    "type_swap": "to",
                    "fee_info": None,
                    "ui_amount": 0.947868014,
                    "price": None,
                    "nearest_price": 215.15213254311675,
                    "change_amount": 947868014,
                    "ui_change_amount": 0.947868014
                },
                "base_price": None,
                "quote_price": 0.026750926577956923,
                "tx_hash": "5yHdeK64gtATtsRSoGaEQ7pMSYb6bdhZhYa6A4H96b144HFcXaux2J96Ym3sN2W4jXL2qUyLbdKQuGgehmHNomQf",
                "source": "raydium",
                "block_unix_time": 1731554982,
                "tx_type": "swap",
                "address": "5QNAD6iofs8K4p7i9pbKty36bfaCixEVJPxBz2d8Y5cy",
                "owner": "GKQBjCn68cTFwUcUiszSioE3B2tAeemfgS2x4Zk2Lyz9"
            }
        ]
        mock_get_trader_trades.return_value = test_data

        actual = await get_traded_tokens_of_trader("", datetime.now(), datetime.now())
        self.assertEqual(2, len(actual))
        self.assertEqual(test_data[0], 'test_1')
        self.assertEqual(test_data[1], 'test_2')


if __name__ == "__main__":
    unittest.main()

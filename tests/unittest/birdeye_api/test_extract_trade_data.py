import unittest
from datetime import datetime

from birdeye_api.trades_endpoint import extract_trade_data
from solana_api.jupiter_api import SOL_MINT


class TestRunner(unittest.TestCase):
    def test_extract_trade_data(self):
        # Given test data
        test_data = {
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
                "address": SOL_MINT,
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

        # When extracting trade data
        result = extract_trade_data(test_data)

        # Then the result should be correct
        expected_result = {
            "trader_id": "GKQBjCn68cTFwUcUiszSioE3B2tAeemfgS2x4Zk2Lyz9",
            "token_sold_amount": 947868014,
            "token_bought_amount": 7623505077,
            "token": "test_1",
            "block_time": datetime.utcfromtimestamp(1731554982),
            "buy": True,
            "launch_time": None,
        }

        self.assertEqual(result, expected_result)

    def test_extract_trade_data_multihop(self):
        # Given test data for a multihop swap (neither base nor quote is SOL)
        test_data = {
            "quote": {"address": "test_token_1", "amount": 1000},
            "base": {"address": "test_token_2", "amount": 500},
            "block_unix_time": 1731554982,
            "owner": "test_owner"
        }

        # When extracting trade data
        result = extract_trade_data(test_data)

        # Then the result should be None
        self.assertIsNone(result)

    def test_extract_trade_data_sell(self):
        # Given test data for a sell (SOL sold for another token)
        test_data = {
            "quote": {
                "symbol": "SOL",
                "decimals": 6,
                "address": SOL_MINT,
                "amount": 7623505077,
                "type": "transfer",
                "type_swap": "to",
                "ui_amount": 7623.505077,
                "price": 0.026750926577956923,
                "nearest_price": 0.026890095180012584,
                "change_amount": -7623505077,
                "ui_change_amount": -7623.505077
            },
            "base": {
                "symbol": "JOAFL",
                "decimals": 9,
                "address": "test_1",
                "amount": 947868014,
                "type": "transfer",
                "type_swap": "from",
                "fee_info": None,
                "ui_amount": 0.947868014,
                "price": None,
                "nearest_price": 215.15213254311675,
                "change_amount": -947868014,
                "ui_change_amount": -0.947868014
            },
            "base_price": None,
            "quote_price": 0.026750926577956923,
            "block_unix_time": 1731554982,
            "tx_hash": "5yHdeK64gtATtsRSoGaEQ7pMSYb6bdhZhYa6A4H96b144HFcXaux2J96Ym3sN2W4jXL2qUyLbdKQuGgehmHNomQf",
            "source": "raydium",
            "tx_type": "swap",
            "address": "5QNAD6iofs8K4p7i9pbKty36bfaCixEVJPxBz2d8Y5cy",
            "owner": "GKQBjCn68cTFwUcUiszSioE3B2tAeemfgS2x4Zk2Lyz9"
        }

        # When extracting trade data
        result = extract_trade_data(test_data)

        # Then the result should be correct
        expected_result = {
            "trader_id": "GKQBjCn68cTFwUcUiszSioE3B2tAeemfgS2x4Zk2Lyz9",
            "token_sold_amount": 947868014,
            "token_bought_amount": 7623505077,
            "token": "test_1",
            "block_time": datetime.utcfromtimestamp(1731554982),
            "buy": False,
            "launch_time": None,
        }

        self.assertEqual(result, expected_result)


if __name__ == "__main__":
    unittest.main()

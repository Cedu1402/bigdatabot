import unittest
import pandas as pd
from pandas.testing import assert_frame_equal
from datetime import datetime, timedelta

from data.combine_price_trades import calculate_minute_positions


class TestRunner(unittest.TestCase):
    def setUp(self):
        """Set up base datetime for consistent testing"""
        self.base_time = datetime(2024, 1, 1, 10, 0, 0)  # 10:00:00

    def create_trade(self, minutes_offset: int, token: str, is_buy: bool, amount: float) -> dict:
        """Helper method to create trade records"""
        return {
            'block_time': self.base_time + timedelta(minutes=minutes_offset),
            'trading_minute': self.base_time + timedelta(minutes=minutes_offset),
            'token': token,
            'buy': 1 if is_buy else 0,
            'token_sold_amount': amount if is_buy else 0,
            'token_bought_amount': amount if not is_buy else 0
        }

    def test_empty_trades(self):
        """Test handling of empty trades DataFrame"""
        empty_df = pd.DataFrame(columns=['block_time', 'trading_minute', 'token', 'buy',
                                         'token_sold_amount', 'token_bought_amount'])

        result = calculate_minute_positions(empty_df)

        expected = pd.DataFrame(columns=['trading_minute', 'token', 'net_position'])
        assert_frame_equal(result, expected)

    def test_single_buy(self):
        """Test single buy trade"""
        trades = pd.DataFrame([
            self.create_trade(0, 'ETH', True, 1.0)
        ])

        result = calculate_minute_positions(trades)

        expected = pd.DataFrame([{
            'trading_minute': self.base_time,
            'token': 'ETH',
            'net_position': 1.0
        }])

        assert_frame_equal(result, expected)

    def test_single_sell(self):
        """Test single sell trade"""
        trades = pd.DataFrame([
            self.create_trade(0, 'ETH', False, 1.0)
        ])

        result = calculate_minute_positions(trades)

        expected = pd.DataFrame([{
            'trading_minute': self.base_time,
            'token': 'ETH',
            'net_position': -1.0
        }])
        assert_frame_equal(result, expected)

    def test_multiple_trades_same_minute(self):
        """Test multiple trades in the same minute"""
        trades = pd.DataFrame([
            self.create_trade(0, 'ETH', True, 1.0),
            self.create_trade(0, 'ETH', True, 2.0),
            self.create_trade(0, 'ETH', False, 0.5)
        ])

        result = calculate_minute_positions(trades)

        expected = pd.DataFrame([{
            'trading_minute': self.base_time,
            'token': 'ETH',
            'net_position': 2.5  # 1.0 + 2.0 - 0.5
        }])
        assert_frame_equal(result, expected)

    def test_different_tokens_same_minute(self):
        """Test trades of different tokens in the same minute"""
        trades = pd.DataFrame([
            self.create_trade(0, 'ETH', True, 1.0),
            self.create_trade(0, 'BTC', False, 0.5)
        ])

        result = calculate_minute_positions(trades).sort_values(['token']).reset_index(drop=True)

        expected = pd.DataFrame([
            {
                'trading_minute': self.base_time,
                'token': 'BTC',
                'net_position': -0.5
            },
            {
                'trading_minute': self.base_time,
                'token': 'ETH',
                'net_position': 1.0
            }
        ])
        assert_frame_equal(result, expected)

    def test_trades_different_minutes(self):
        """Test trades across different minutes"""
        trades = pd.DataFrame([
            self.create_trade(0, 'ETH', True, 1.0),
            self.create_trade(1, 'ETH', False, 0.5),
            self.create_trade(2, 'ETH', True, 0.3)
        ])

        result = calculate_minute_positions(trades)

        expected = pd.DataFrame([
            {
                'trading_minute': self.base_time,
                'token': 'ETH',
                'net_position': 1.0
            },
            {
                'trading_minute': self.base_time + timedelta(minutes=1),
                'token': 'ETH',
                'net_position': -0.5
            },
            {
                'trading_minute': self.base_time + timedelta(minutes=2),
                'token': 'ETH',
                'net_position': 0.3
            }
        ])
        assert_frame_equal(result, expected)

    def test_edge_case_zero_amounts(self):
        """Test handling of zero amount trades"""
        trades = pd.DataFrame([
            self.create_trade(0, 'ETH', True, 0.0),
            self.create_trade(0, 'ETH', False, 0.0)
        ])

        result = calculate_minute_positions(trades)

        expected = pd.DataFrame([{
            'trading_minute': self.base_time,
            'token': 'ETH',
            'net_position': 0.0
        }])
        assert_frame_equal(result, expected)


if __name__ == '__main__':
    unittest.main()

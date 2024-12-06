import unittest
from datetime import datetime

from data.combine_price_trades import TraderState
from data.trade_data import get_trade_state_no_trade_in_minute
from solana_api.trade_model import Trade


class TestRunner(unittest.TestCase):
    def test_no_previous_state_and_last_trade_buy(self):
        last_trade_state = TraderState.NO_ACTION
        last_trade = Trade(
            trader="trader1",
            token="token1",
            token_amount=100,
            sol_amount=2,
            buy=True,
            token_holding_after=5,
            trade_time=datetime(2024, 11, 30, 15, 30).isoformat(),
        )
        result = get_trade_state_no_trade_in_minute(last_trade_state, last_trade)
        self.assertEqual(result, TraderState.STILL_HOLDS)

    def test_previous_state_just_bought(self):
        last_trade_state = TraderState.JUST_BOUGHT
        last_trade = Trade(
            trader="trader1",
            token="token1",
            token_amount=50,
            sol_amount=1,
            buy=False,
            token_holding_after=2,
            trade_time=datetime(2024, 11, 30, 15, 31).isoformat(),
        )
        result = get_trade_state_no_trade_in_minute(last_trade_state, last_trade)
        self.assertEqual(result, TraderState.STILL_HOLDS)

    def test_previous_state_just_sold(self):
        last_trade_state = TraderState.JUST_SOLD
        last_trade = Trade(
            trader="trader1",
            token="token1",
            token_amount=0,
            sol_amount=0,
            buy=False,
            token_holding_after=0,
            trade_time=datetime(2024, 11, 30, 15, 32).isoformat(),
        )
        result = get_trade_state_no_trade_in_minute(last_trade_state, last_trade)
        self.assertEqual(result, TraderState.STILL_HOLDS)

    def test_previous_state_nuked(self):
        last_trade_state = TraderState.NUKED
        last_trade = Trade(
            trader="trader1",
            token="token1",
            token_amount=0,
            sol_amount=0,
            buy=False,
            token_holding_after=0,
            trade_time=datetime(2024, 11, 30, 15, 33).isoformat(),
        )
        result = get_trade_state_no_trade_in_minute(last_trade_state, last_trade)
        self.assertEqual(result, TraderState.SOLD_ALL)

    def test_no_action(self):
        last_trade_state = TraderState.NO_ACTION
        last_trade = Trade(
            trader="trader1",
            token="token1",
            token_amount=0,
            sol_amount=0,
            buy=False,
            token_holding_after=0,
            trade_time=datetime(2024, 11, 30, 15, 34).isoformat(),
        )
        result = get_trade_state_no_trade_in_minute(last_trade_state, last_trade)
        self.assertEqual(result, TraderState.NO_ACTION)


if __name__ == "__main__":
    unittest.main()

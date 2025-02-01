from typing import List

from constants import MAX_MCTS_STEPS
from mcts.action import TradeAction
from mcts.trades import run_buy_action, run_sell_action


class State:

    def __init__(self, base_token_price_changes: List[float],
                 token_price: float, initial_value: float, action: TradeAction, previous_holding: float,
                 previous_step: int):

        self.base_token_price_changes = base_token_price_changes
        self.token_price = token_price
        self.initial_value = initial_value
        self.action = action
        self.current_step = previous_step + 1
        self.token_holding = previous_holding

        self.return_of_investment = 0.0
        self.run_action(previous_holding)

    def run_action(self, previous_holding):
        if self.action == TradeAction.BUY:
            self.token_holding = run_buy_action(self.initial_value, self.token_price)
        elif self.action == TradeAction.SELL:
            self.return_of_investment = run_sell_action(self.token_holding, self.token_price) - self.initial_value
            self.token_holding = 0.0

    def is_end_state(self) -> bool:
        return self.action == TradeAction.SELL or self.current_step >= MAX_MCTS_STEPS

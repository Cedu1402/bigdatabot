from typing import Tuple, Optional

from constants import MAX_MCTS_STEPS, CURRENT_ASSET_PRICE_COLUMN
from mcts.action import TradeAction
from mcts.child_node_sampling import get_next_price
from mcts.info_set import InfoSet
from mcts.trades import run_buy_action, run_sell_action


def calculate_reward_by_price(token_price: float, token_holding: float, investment: float) -> Tuple[float, float]:
    sell_value = run_sell_action(token_holding, token_price)
    return_of_investment = sell_value - investment
    reward = return_of_investment

    if reward >= 4 or reward < -5:
        reward *= 2

    return reward, return_of_investment


class State:

    def __init__(self, info_set_index: int, investment: float, action: TradeAction,
                 info_set_buy_index: int, previous_step: int, fixed_holding: Optional[float]):

        self.info_set_index = info_set_index
        self.investment = investment
        self.action = action
        self.current_step = previous_step + 1
        self.info_set_buy_index = info_set_buy_index
        self.fixed_holding = fixed_holding

        if action == TradeAction.BUY:
            self.info_set_buy_index = info_set_index

        self.return_of_investment = 0.0
        self.reward = 0.0

    def calculate_reward(self):
        token_price = get_next_price(self.info_set_index)
        token_holding = self.get_holding()
        self.reward, self.return_of_investment = calculate_reward_by_price(token_price, token_holding,
                                                                           self.investment)

    def is_end_state(self) -> bool:
        return self.action == TradeAction.SELL or self.current_step >= MAX_MCTS_STEPS

    def get_holding(self):
        if self.fixed_holding:
            return self.fixed_holding

        if self.info_set_buy_index != -1:
            return run_buy_action(self.investment,
                                  InfoSet().get_info_set()[CURRENT_ASSET_PRICE_COLUMN][self.info_set_buy_index])

        return 0.0

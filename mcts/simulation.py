from typing import List

from constants import CURRENT_ASSET_PRICE_COLUMN
from mcts.action import TradeAction
from mcts.info_set import InfoSet
from mcts.state import State, calculate_reward_by_price
from mcts.trades import run_buy_action


def get_possible_actions(state) -> List[TradeAction]:
    if state.action == TradeAction.BUY:
        return [TradeAction.DO_NOTHING, TradeAction.SELL]
    elif state.action == TradeAction.SELL:
        return []
    else:
        possible_action = TradeAction.BUY if state.get_holding() == 0 else TradeAction.SELL
        return [possible_action, TradeAction.DO_NOTHING]


def simulate_no_holding(current_index: int, investment: float) -> float:
    base_token_price_changes = InfoSet().get_info_set()[current_index:]

    min_index = base_token_price_changes[CURRENT_ASSET_PRICE_COLUMN][:int(len(base_token_price_changes) / 2)].idxmin()
    min_value = base_token_price_changes.loc[min_index, CURRENT_ASSET_PRICE_COLUMN]
    max_value = base_token_price_changes[min_index + 1:][CURRENT_ASSET_PRICE_COLUMN].max() * 0.9
    if max_value != max_value:
        print("here")

    token_amount = run_buy_action(investment, min_value)

    reward, _ = calculate_reward_by_price(max_value, token_amount, investment)

    return reward


def simulate_best_exit(current_index: int, investment: float, token_amount: float) -> float:
    base_token_price_changes = InfoSet().get_info_set()[current_index:]
    max_value = base_token_price_changes[CURRENT_ASSET_PRICE_COLUMN].max() * 0.9

    reward, _ = calculate_reward_by_price(max_value, token_amount, investment)
    return reward


def unroll_simulation(current_state: State) -> float:
    # 1. if nothing bought get min price in next x min and max after min price
    if current_state.action == TradeAction.DO_NOTHING and current_state.get_holding() == 0:
        return simulate_no_holding(current_state.info_set_index, current_state.investment)

    # 2. if bought get max price in future
    if current_state.action != TradeAction.SELL and current_state.get_holding() > 0:
        return simulate_best_exit(current_state.info_set_index, current_state.investment,
                                  current_state.get_holding())

    # 3. if sold just return the reward
    current_state.calculate_reward()
    return current_state.reward

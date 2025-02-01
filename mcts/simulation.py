import random
from typing import List

from mcts.action import TradeAction
from mcts.child_node_sampling import get_next_price, get_next_percentage_change
from mcts.state import State


def get_possible_actions(state) -> List[TradeAction]:
    if state.action == TradeAction.BUY:
        return [TradeAction.DO_NOTHING, TradeAction.SELL]
    elif state.action == TradeAction.SELL:
        return []
    else:
        possible_action = TradeAction.BUY if state.token_holding == 0 else TradeAction.SELL
        return [possible_action, TradeAction.DO_NOTHING]


def unroll_simulation(current_state: State) -> float:
    current_price = current_state.token_price
    base_token_price_changes = current_state.base_token_price_changes

    while True:
        base_token_price_changes = get_next_percentage_change(base_token_price_changes)
        current_price = get_next_price(current_price, base_token_price_changes[0])
        selected_action = random.choice(get_possible_actions(current_state))
        
        current_state = State(base_token_price_changes, current_price, current_state.initial_value, selected_action,
                              current_state.token_holding, current_state.current_step)

        if current_state.is_end_state():
            break

    return current_state.return_of_investment

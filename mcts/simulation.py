import random

from mcts.action import TRADE_ACTIONS, SELL_ACTION


def unroll_simulation(current_state, base_movement, fluctuation):
    selected_actions = list()
    while True:
        selected_action = random.choice(TRADE_ACTIONS)
        if selected_action == SELL_ACTION:
            break
        
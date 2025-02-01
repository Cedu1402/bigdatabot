import random
from datetime import datetime
from typing import List

from mcts.action import TradeAction
from mcts.node import Node
from mcts.state import State


class MonteCarloSearchTree:

    def __init__(self, info_sets: List[List[float]], token_price: float, investment_amount: float,
                 previous_holding: float, previous_step: int, previous_action: TradeAction):

        self.start_state = State(info_sets[0], token_price, investment_amount,
                                 previous_action, previous_holding, previous_step)

        self.root = Node(None, self.start_state)
        self.info_sets = info_sets

    def set_info_set(self):
        info_set = random.choice(self.info_sets)
        self.root.state.base_token_price_changes = info_set

    def evaluate_tree(self, max_run_time: int):
        # todo add random noise to price change or black swan event based on some possibility.
        sample_info_set_max = 5000
        sample_info_set_count = sample_info_set_max
        info_set_count = 0
        start_time = datetime.now()
        while (datetime.now() - start_time).total_seconds() < max_run_time:
            if sample_info_set_count == sample_info_set_max:
                sample_info_set_count = 0
                self.set_info_set()
                info_set_count += 1

            self.root.selection()
            sample_info_set_count += 1

        print(f"Info sets visited: {info_set_count}")

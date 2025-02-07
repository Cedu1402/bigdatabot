from datetime import datetime
from typing import Optional

from mcts.action import TradeAction
from mcts.info_set import InfoSet
from mcts.node import Node
from mcts.state import State


class MonteCarloSearchTree:

    def __init__(self, investment_amount: float,
                 previous_holding: Optional[float], previous_step: int, previous_action: TradeAction):

        self.info_set = InfoSet()
        self.info_set.set_random_info_set()

        self.start_state = State(0, investment_amount,
                                 previous_action, -1, previous_step, previous_holding)

        self.root = Node(None, self.start_state)

    def evaluate_tree(self, max_run_time: int):
        # todo add random noise to price change or black swan event based on some possibility.
        sample_info_set_max = 750
        sample_info_set_count = sample_info_set_max
        info_set_count = 0
        start_time = datetime.now()
        while (datetime.now() - start_time).total_seconds() < max_run_time:
            if sample_info_set_count == sample_info_set_max:
                sample_info_set_count = 0
                self.info_set.set_random_info_set()
                info_set_count += 1

            self.root.selection()
            sample_info_set_count += 1

        print(f"Info sets visited: {info_set_count}")

    def get_depth(self) -> int:
        return self.root.get_max_depth()

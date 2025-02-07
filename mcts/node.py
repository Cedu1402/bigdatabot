from typing import List, Optional

from mcts.child_node_sampling import ucb1
from mcts.simulation import unroll_simulation, get_possible_actions
from mcts.state import State


def node_expansion(parent_node: "Node") -> List["Node"]:
    parent_state = parent_node.state
    possible_actions = get_possible_actions(parent_state)
    child_nodes = list()

    for action in possible_actions:
        child_state = State(parent_node.state.info_set_index + 1,
                            parent_state.investment, action,
                            parent_state.info_set_buy_index, parent_state.current_step, parent_state.fixed_holding)

        child_nodes.append(Node(parent_node, child_state))

    return child_nodes


class Node:

    def __init__(self, parent_node: Optional["Node"], state: State):

        self.state = state
        self.children = list()
        self.parent = parent_node
        self.reward_value = 0
        self.visit_count = 0

    def expansion(self):
        self.children = node_expansion(self)

    def selection(self):
        if self.is_terminal_node():
            self.state.calculate_reward()
            return self.backpropagation(self.state.reward)

        if self.is_node_unexplored() and self.parent:
            reward = self.run_simulation()
            return self.backpropagation(reward)

        if len(self.children) == 0:
            self.expansion()

        best_node = self.child_node_selection()
        best_node.selection()

    def child_node_selection(self) -> Optional["Node"]:
        return max(self.children,
                   key=lambda c: ucb1(c.reward_value, c.visit_count, self.visit_count))

    def is_node_unexplored(self) -> bool:
        return self.visit_count == 0

    def backpropagation(self, reward: float):
        self.visit_count += 1
        self.reward_value += reward

        if self.parent:
            self.parent.backpropagation(reward)

    def run_simulation(self) -> float:
        return unroll_simulation(self.state)

    def is_terminal_node(self) -> bool:
        return self.state.is_end_state()

    def get_max_depth(self) -> int:
        if not self.children:
            return 1  # leaf node counts as depth 1
        return 1 + max(child.get_max_depth() for child in self.children)

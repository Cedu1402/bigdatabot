from typing import List, Optional

from mcts.child_node_sampling import ucb1, get_next_percentage_change, get_next_price
from mcts.simulation import unroll_simulation, get_possible_actions
from mcts.state import State


def node_expansion(parent_node: "Node") -> List["Node"]:
    parent_state = parent_node.state
    base_token_price_changes = get_next_percentage_change(parent_state.base_token_price_changes)
    node_token_price = get_next_price(parent_state.token_price, base_token_price_changes[0])

    possible_actions = get_possible_actions(parent_state)
    child_nodes = list()

    for action in possible_actions:
        child_state = State(base_token_price_changes, node_token_price, parent_state.initial_value, action,
                            parent_state.token_holding, parent_state.current_step)

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
            return self.backpropagation(self.state.return_of_investment)

        if self.is_node_unexplored() and self.parent:
            reward = self.run_simulation()
            self.backpropagation(reward)
            return

        if len(self.children) == 0:
            self.expansion()

        best_node = self.child_node_selection()
        best_node.selection()

    def child_node_selection(self) -> "Node":
        return max(self.children, key=lambda c: ucb1(c.reward_value, c.visit_count, self.visit_count))

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

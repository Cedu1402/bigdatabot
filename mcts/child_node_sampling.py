import math
from typing import List


def get_next_price(token_price: float, change_pct: float) -> float:
    return token_price * (1 + change_pct)


def get_next_percentage_change(base_token_price_changes: List[float]) -> List[float]:
    return base_token_price_changes[1:]


def ucb1(node_value, node_visits, parent_visits, exploration_constant=2.0):
    """
    Compute the UCB1 score.

    Parameters:
    - node_value (float): The total reward for the node.
    - node_visits (int): Number of times the node was visited.
    - parent_visits (int): Number of visits to the parent node.
    - exploration_constant (float): Constant to balance exploration and exploitation.

    Returns:
    - float: UCB1 score.
    """
    if node_visits == 0:
        return float('inf')  # Explore unvisited nodes first

    exploitation = node_value / node_visits
    exploration = exploration_constant * math.sqrt(math.log(parent_visits) / node_visits)

    return exploitation + exploration

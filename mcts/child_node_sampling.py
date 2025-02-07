import math

from constants import PRICE_PCT_CHANGE, CURRENT_ASSET_PRICE_COLUMN
from mcts.info_set import InfoSet


def get_next_pct_change(at_index: int) -> float:
    return InfoSet().get_info_set()[PRICE_PCT_CHANGE].iloc[at_index]


def get_next_price(at_index: int) -> float:
    return InfoSet().get_info_set()[CURRENT_ASSET_PRICE_COLUMN].iloc[at_index]


def ucb1(node_value, node_visits, parent_visits, exploration_constant=200.0):
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

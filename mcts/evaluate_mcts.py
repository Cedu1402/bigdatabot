import random
from datetime import datetime
from typing import List

import pandas as pd

from constants import TRADING_MINUTE_COLUMN, TOKEN_COlUMN, PRICE_COLUMN, RANDOM_SEED
from data.random_seed import set_random_seed
from mcts.action import TradeAction
from mcts.token_sample import load_token_ohlcv_data, sample_random_tokens, add_price_pct_column, get_info_sets
from mcts.trades import run_buy_action, run_sell_action
from mcts.tree import MonteCarloSearchTree


def get_validation_tokens(data: pd.DataFrame, amount: int) -> List[pd.DataFrame]:
    max_date = datetime(2024, 11, 30)
    min_date = datetime(2024, 11, 15)

    possible_tokens = list(data[(data[TRADING_MINUTE_COLUMN] < max_date) & (data[TRADING_MINUTE_COLUMN] >= min_date)][
                               TOKEN_COlUMN].unique())

    selected_tokens = random.sample(possible_tokens, amount if len(possible_tokens) > amount else len(possible_tokens))
    print("Amount of tokens selected:", len(selected_tokens))
    return [group for _, group in data[data[TOKEN_COlUMN].isin(selected_tokens)].groupby(TOKEN_COlUMN)]


def run_mcts_on_validation():
    ohlcv_data = load_token_ohlcv_data()
    validation_tokens = get_validation_tokens(ohlcv_data, 500)
    ohlcv_data = add_price_pct_column(ohlcv_data)
    total_return = 0

    for token_data in validation_tokens:
        token_start_date = token_data[TRADING_MINUTE_COLUMN].min()
        token = token_data[TOKEN_COlUMN].iloc[0]

        current_holding = 0
        current_step = 0
        last_action = TradeAction.DO_NOTHING

        info_sets = sample_random_tokens(token, ohlcv_data, 500, token_start_date)
        info_sets = get_info_sets(info_sets)
        investment_amount = 10

        for index, row in token_data.iterrows():
            token_price = row[PRICE_COLUMN]
            current_step += 1
            mcts = MonteCarloSearchTree(info_sets, token_price, investment_amount, current_holding, current_step,
                                        last_action)
            mcts.evaluate_tree(10)
            for child in mcts.root.children:
                print(child.state.action, child.visit_count, child.reward_value)

            last_action = max(mcts.root.children, key=lambda x: x.visit_count).state.action
            if last_action == TradeAction.BUY:
                current_holding = run_buy_action(investment_amount,
                                                 token_price)  # todo add a increase as we do not buy directly at close as we need time to run the sim.
            elif last_action == TradeAction.SELL:
                return_of_investment = run_sell_action(current_holding, token_price) - investment_amount
                print(f"Profit for token {return_of_investment} $")
                total_return += return_of_investment
                print(f"Current total return {total_return} $")
                break

    print(f"Total return $ {total_return}")


if __name__ == '__main__':
    set_random_seed(RANDOM_SEED)
    run_mcts_on_validation()

import logging
from typing import List

import pandas as pd

from constants import INVESTMENT_AMOUNT

logger = logging.getLogger(__name__)


def run_simulation(val_x: pd.DataFrame, val_y: List[bool], prediction: List[bool]):
    ape_amount = INVESTMENT_AMOUNT
    total_return = 0
    token_bought = list()
    good_trades = 0
    bad_trades = 0

    for index, data in val_x.iterrows():
        if not prediction[index]:
            continue

        token = data["token"]
        if token not in token_bought:
            token_bought.append(token)
            if val_y[index]:
                total_return += ape_amount
                good_trades += 1
            else:
                total_return += -(ape_amount / 2)
                bad_trades += 1

    logger.info(f"Total return: {total_return}, Good trades: {good_trades}, Bad trades: {bad_trades}")

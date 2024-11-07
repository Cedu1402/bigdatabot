from typing import List, Dict

import pandas as pd

from constants import TRADING_MINUTE_COLUMN, PRICE_COLUMN, BUY_VOLUME_COLUMN, SELL_VOLUME_COLUMN, TOTAL_VOLUME_COLUMN


class BaseModel:

    def __init__(self, config: Dict):
        self.non_training_columns = [
            TRADING_MINUTE_COLUMN,
            PRICE_COLUMN,
            BUY_VOLUME_COLUMN,
            SELL_VOLUME_COLUMN,
            TOTAL_VOLUME_COLUMN,
        ]

    def build_model(self):
        return

    def prepare_data(self, train: List[pd.DataFrame], val: List[pd.DataFrame], test: List[pd.DataFrame]):
        return

    def train(self):
        return

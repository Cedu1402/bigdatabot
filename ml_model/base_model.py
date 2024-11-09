from typing import List, Dict

import pandas as pd

from constants import TRADING_MINUTE_COLUMN, PRICE_COLUMN, BUY_VOLUME_COLUMN, SELL_VOLUME_COLUMN, TOTAL_VOLUME_COLUMN, \
    TOKEN_COlUMN, MARKET_CAP_USD


class BaseModel:

    def __init__(self, config: Dict):
        self.non_training_columns = [
            TRADING_MINUTE_COLUMN,
            PRICE_COLUMN,
            BUY_VOLUME_COLUMN,
            SELL_VOLUME_COLUMN,
            TOTAL_VOLUME_COLUMN,
            TOKEN_COlUMN,
            MARKET_CAP_USD
        ]

    def build_model(self):
        return

    def prepare_data(self, train: List[pd.DataFrame], val: List[pd.DataFrame], test: List[pd.DataFrame]):
        return

    def train(self, train_x: List[pd.DataFrame], train_y: List, val_x: List[pd.DataFrame], val_y: List):
        return

    def save(self):
        return

    def load_model(self, name):
        return

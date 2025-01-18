from typing import List, Dict

import pandas as pd

from constants import TRADING_MINUTE_COLUMN, BUY_VOLUME_COLUMN, SELL_VOLUME_COLUMN, LAUNCH_DATE_COLUMN


class BaseModelBuilder:

    def __init__(self, config: Dict):
        self.non_training_columns = [
            TRADING_MINUTE_COLUMN,
            BUY_VOLUME_COLUMN,
            SELL_VOLUME_COLUMN,
            LAUNCH_DATE_COLUMN
        ]

    def build_model(self):
        return

    def prepare_data(self, train: List[pd.DataFrame], val: List[pd.DataFrame], test: List[pd.DataFrame]):
        return

    def train(self, train_data: pd.DataFrame, val_data: pd.DataFrame):
        return

    def save(self):
        return

    def load_model(self, name):
        return

    def get_model(self):
        return

from typing import Dict

import pandas as pd

from constants import TRADING_MINUTE_COLUMN, BUY_VOLUME_COLUMN, SELL_VOLUME_COLUMN, LAUNCH_DATE_COLUMN


class BaseModelBuilder:

    def __init__(self, config: Dict):
        self.config = config
        self.non_training_columns = [
            TRADING_MINUTE_COLUMN,
            BUY_VOLUME_COLUMN,
            SELL_VOLUME_COLUMN,
            LAUNCH_DATE_COLUMN
        ]

    def build_model(self):
        return

    def prepare_dataset(self, data: pd.DataFrame, sorted_data: bool):
        return

    def prepare_prediction_data(self, data: pd.DataFrame, validation: bool):
        return

    def train(self, train_data: pd.DataFrame, val_data: pd.DataFrame):
        return

    def save(self):
        return

    def load_model(self, name):
        return

    def get_model(self):
        return

from typing import Dict

import pandas as pd

from constants import BUY_VOLUME_COLUMN, SELL_VOLUME_COLUMN, LAUNCH_DATE_COLUMN


class BaseModelBuilder:

    def __init__(self, config: Dict):
        self.config = config
        self.non_training_columns = [
            BUY_VOLUME_COLUMN,
            SELL_VOLUME_COLUMN,
            LAUNCH_DATE_COLUMN
        ]
        self.columns = list()

    def get_columns(self):
        return self.columns

    def build_model(self, config: Dict = None):
        return

    def prepare_dataset(self, data: pd.DataFrame, sorted_data: bool):
        return data

    def prepare_prediction_data(self, data: pd.DataFrame, validation: bool):
        return data

    def train(self, train_data: pd.DataFrame, val_data: pd.DataFrame):
        return

    def save(self):
        return

    def load_model(self, name):
        return

    def get_model(self):
        return

    def predict(self, data):
        return
from typing import Dict

import pandas as pd

from constants import LABEL_COLUMN, TOKEN_COlUMN, TRADING_MINUTE_COLUMN
from evaluation.simulate_trade import run_simulation
from ml_model.base_model import BaseModelBuilder
from ml_model.model_evaluation import print_evaluation


class BuyAllModel(BaseModelBuilder):

    def __init__(self, config: Dict):
        super().__init__(config)

    def train(self, train_data: pd.DataFrame, val_data: pd.DataFrame):
        val_data.sort_values(by=[TOKEN_COlUMN, TRADING_MINUTE_COLUMN], inplace=True)
        val_data.reset_index(inplace=True, drop=True)

        val_predictions = self.predict(val_data)


        print_evaluation(val_data[LABEL_COLUMN], val_predictions)
        run_simulation(val_data, val_data[LABEL_COLUMN], val_predictions, self.config)

    def predict(self, data):
        return [True for _ in range(len(data))]

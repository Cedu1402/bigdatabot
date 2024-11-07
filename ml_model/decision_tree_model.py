from typing import List, Dict

import pandas as pd

from constants import BIN_AMOUNT_KEY, PRICE_PCT_CHANGE, BUY_VOLUME_PCT_CHANGE, SELL_VOLUME_PCT_CHANGE, \
    TOTAL_VOLUME_PCT_CHANGE, PERCENTAGE_OF_1_MILLION_MARKET_CAP
from data.feature_engineering import compute_bin_edges, bin_data
from data.model_data import remove_columns
from data.sliding_window import unroll_data
from ml_model.base_model import BaseModel


class DecisionTreeModel(BaseModel):

    def __init__(self, config: Dict):
        self.bin_amount = config[BIN_AMOUNT_KEY]
        self.bin_edges = dict()
        self.bined_columns = [PRICE_PCT_CHANGE, BUY_VOLUME_PCT_CHANGE,
                              SELL_VOLUME_PCT_CHANGE, TOTAL_VOLUME_PCT_CHANGE,
                              PERCENTAGE_OF_1_MILLION_MARKET_CAP]

    def prepare_data(self, train: List[pd.DataFrame], val: List[pd.DataFrame], test: List[pd.DataFrame]):
        # remove unused columns
        train = remove_columns(train, self.non_training_columns)
        val = remove_columns(val, self.non_training_columns)
        test = remove_columns(test, self.non_training_columns)

        # bin data of used columns
        full_train_data = unroll_data(train)
        self.bin_edges = compute_bin_edges(full_train_data, self.bined_columns, self.bin_amount)
        train = bin_data(train, self.bined_columns, self.bin_edges)
        val = bin_data(val, self.bined_columns, self.bin_edges)
        test = bin_data(test, self.bined_columns, self.bin_edges)

        # split data into x, y
        train_x, train_y, val_x, val_y, test_x, test_y = unroll_data(train)

        return train_x, train_y, val_x, val_y, test_x, test_y

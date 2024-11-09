import os.path
from typing import List, Dict, Tuple

import pandas as pd
from sklearn.tree import DecisionTreeClassifier

from constants import BIN_AMOUNT_KEY, PRICE_PCT_CHANGE, BUY_VOLUME_PCT_CHANGE, SELL_VOLUME_PCT_CHANGE, \
    TOTAL_VOLUME_PCT_CHANGE, PERCENTAGE_OF_1_MILLION_MARKET_CAP, RANDOM_SEED, MODEL_FOLDER
from data.data_split import get_x_y_data, flatten_dataframe_list
from data.feature_engineering import compute_bin_edges, bin_data
from data.model_data import remove_columns
from data.pickle_files import save_to_pickle
from data.sliding_window import unroll_data
from ml_model.base_model import BaseModel
from ml_model.load_model import load_model
from ml_model.model_evaluation import print_evaluation


class DecisionTreeModel(BaseModel):

    def __init__(self, config: Dict):
        super().__init__(config)
        self.bin_amount = config[BIN_AMOUNT_KEY]
        self.bin_edges = dict()
        self.binned_columns = [PRICE_PCT_CHANGE, BUY_VOLUME_PCT_CHANGE,
                               SELL_VOLUME_PCT_CHANGE, TOTAL_VOLUME_PCT_CHANGE,
                               PERCENTAGE_OF_1_MILLION_MARKET_CAP]
        self.model = None

    def build_model(self):
        self.model = DecisionTreeClassifier(random_state=RANDOM_SEED)

    def prepare_data(self, train: List[pd.DataFrame], val: List[pd.DataFrame], test: List[pd.DataFrame]) -> (
            Tuple)[List[pd.DataFrame], List, List[pd.DataFrame], List, List[pd.DataFrame], List]:
        # remove unused columns
        train = remove_columns(train, self.non_training_columns)
        val = remove_columns(val, self.non_training_columns)
        test = remove_columns(test, self.non_training_columns)

        # bin data of used columns
        full_train_data = unroll_data(train)
        self.bin_edges = compute_bin_edges(full_train_data, self.binned_columns, self.bin_amount)
        train = bin_data(train, self.binned_columns, self.bin_edges)
        val = bin_data(val, self.binned_columns, self.bin_edges)
        test = bin_data(test, self.binned_columns, self.bin_edges)

        # split data into x, y
        train_x, train_y, val_x, val_y, test_x, test_y = get_x_y_data(train, val, test)

        return train_x, train_y, val_x, val_y, test_x, test_y

    def train(self, train_x: List[pd.DataFrame], train_y: List, val_x: List[pd.DataFrame], val_y: List):
        # flatten take only the last item of each dataframe
        train_x = flatten_dataframe_list(train_x)
        self.model.fit(train_x, train_y)

        # evaluate
        val_x = flatten_dataframe_list(val_x)
        val_predictions = self.model.predict(val_x)
        print_evaluation(val_y, val_predictions)

    def save(self):
        save_to_pickle(self.model, os.path.join(MODEL_FOLDER, "simple_tree.pkl"))

    def load_model(self, name):
        self.model = load_model(name)

    def predict(self, data):
        data = flatten_dataframe_list(data)
        return self.model.predict(data)

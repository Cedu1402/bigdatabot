import os.path
from typing import List, Dict, Tuple, Optional

import pandas as pd
from sklearn.tree import DecisionTreeClassifier

from constants import BIN_AMOUNT_KEY, PRICE_PCT_CHANGE, BUY_VOLUME_PCT_CHANGE, SELL_VOLUME_PCT_CHANGE, \
    TOTAL_VOLUME_PCT_CHANGE, PERCENTAGE_OF_1_MILLION_MARKET_CAP, RANDOM_SEED, MODEL_FOLDER
from data.data_split import get_x_y_data, flatten_dataframe_list, get_x_y_of_list
from data.feature_engineering import compute_bin_edges, bin_data
from data.model_data import remove_columns, order_columns
from data.pickle_files import save_to_pickle
from data.sliding_window import unroll_data
from ml_model.base_model import BaseModel
from ml_model.load_model import load_model
from ml_model.model_evaluation import print_evaluation
import logging
logger = logging.getLogger(__name__)

class DecisionTreeModel(BaseModel):

    def __init__(self, config: Dict):
        super().__init__(config)
        self.bin_amount = config[BIN_AMOUNT_KEY]
        self.bin_edges = dict()
        self.columns = list()
        self.binned_columns = [PRICE_PCT_CHANGE, BUY_VOLUME_PCT_CHANGE,
                               SELL_VOLUME_PCT_CHANGE, TOTAL_VOLUME_PCT_CHANGE,
                               PERCENTAGE_OF_1_MILLION_MARKET_CAP]
        self.model = None

    def get_columns(self):
        return self.columns
    
    def build_model(self):
        self.model = DecisionTreeClassifier(random_state=RANDOM_SEED, max_depth=10, ccp_alpha=0.01)

    def prepare_train_data(self, train: List[pd.DataFrame], val: List[pd.DataFrame], test: List[pd.DataFrame]) -> (
            Tuple)[List[pd.DataFrame], List, List[pd.DataFrame], List, List[pd.DataFrame], List]:
        # remove unused columns
        logger.info("Remove unused columns from data")
        train = remove_columns(train, self.non_training_columns)
        val = remove_columns(val, self.non_training_columns)
        test = remove_columns(test, self.non_training_columns)

        # bin data of used columns
        logger.info("Unroll data")
        full_train_data = unroll_data(train)
        logger.info("Calculate edges of binned data")
        self.bin_edges = compute_bin_edges(full_train_data, self.binned_columns, self.bin_amount)
        logger.info("Bin data")
        train = bin_data(train, self.binned_columns, self.bin_edges)
        val = bin_data(val, self.binned_columns, self.bin_edges)
        test = bin_data(test, self.binned_columns, self.bin_edges)

        # split data into x, y
        logger.info("Split data into x and y sets for training and evaluation")
        train_x, train_y, val_x, val_y, test_x, test_y = get_x_y_data(train, val, test)
        logger.info("Extract column order for inferance")
        self.columns = list(train_x[0].columns)

        return train_x, train_y, val_x, val_y, test_x, test_y

    def prepare_prediction_data(self, data: List[pd.DataFrame], contains_label: bool) -> Tuple[
        List[pd.DataFrame], Optional[List]]:
        logger.info("Remove unused columns")
        data = remove_columns(data, self.non_training_columns)
        logger.info("Bin data")
        full_data = bin_data(data, self.binned_columns, self.bin_edges)
        y_data = None
        if contains_label:
            logger.info("Split into x and y set")
            x_data, y_data = get_x_y_of_list(full_data)
        logger.info("Sort order like it was trained")
        x_data = order_columns(full_data, self.columns)
        return x_data, y_data

    def train(self, train_x: List[pd.DataFrame], train_y: List, val_x: List[pd.DataFrame], val_y: List):
        # flatten take only the last item of each dataframe
        logger.info("Flatten data for training")
        train_x = flatten_dataframe_list(train_x)
        logger.info("Train model")
        self.model.fit(train_x, train_y)

        # evaluate
        logger.info("Fatten evaluation data")
        val_x = flatten_dataframe_list(val_x)
        logger.info("Predict evaluation data")
        val_predictions = self.model.predict(val_x)
        logger.info("Print evaluation results")
        print_evaluation(val_y, val_predictions)

    def save(self):
        save_to_pickle((self.model, self.bin_edges, self.columns), os.path.join(MODEL_FOLDER, "simple_tree.pkl"))

    def load_model(self, name):
        self.model, self.bin_edges, self.columns = load_model(name)

    def predict(self, data):
        data = flatten_dataframe_list(data)
        return self.model.predict(data)

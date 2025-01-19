import logging
import os.path
from typing import Dict, Tuple, List

import pandas as pd
from sklearn.tree import DecisionTreeClassifier

from constants import BIN_AMOUNT_KEY, PRICE_PCT_CHANGE, BUY_VOLUME_PCT_CHANGE, SELL_VOLUME_PCT_CHANGE, \
    TOTAL_VOLUME_PCT_CHANGE, PERCENTAGE_OF_1_MILLION_MARKET_CAP, RANDOM_SEED, MODEL_FOLDER, PRICE_COLUMN, \
    CHANGE_FROM_ATL, CHANGE_FROM_ATH, CUMULATIVE_VOLUME, AGE_IN_MINUTES_COLUMN, TOTAL_VOLUME_COLUMN, \
    N_FEATURES_TO_SELECT, RFE_STEP_SIZE, CRITERION, TOKEN_COlUMN, STEP_SIZE_KEY, LABEL_COLUMN, MAX_DEPTH
from data.data_split import flatten_dataframe_list
from data.feature_engineering import bin_data, compute_bin_edges
from data.model_data import remove_columns_dataframe
from data.pickle_files import save_to_pickle
from data.sliding_window import create_sliding_window_flat
from evaluation.simulate_trade import run_simulation
from ml_model.base_model import BaseModelBuilder
from ml_model.load_model import load_model
from ml_model.model_evaluation import print_evaluation
from ml_model.sk_learn_training_loop import train_loop

logger = logging.getLogger(__name__)


def get_tree_hyperparameters(config: dict) -> dict:
    return {
        # Dataset and RFE parameters
        'data_preprocess__' + BIN_AMOUNT_KEY: config.get(BIN_AMOUNT_KEY, [1000, 2000, 5000]),
        # 'data_preprocess__' + STEP_SIZE_KEY: config.get(STEP_SIZE_KEY, [1]),
        'rfe__' + N_FEATURES_TO_SELECT: config.get(N_FEATURES_TO_SELECT, [79]),
        'rfe__step': config.get(RFE_STEP_SIZE, [1]),

        # Tree hyperparameters
        'classifier__' + MAX_DEPTH: config.get(MAX_DEPTH, [5, 10, 15, None]),
        # 'classifier__' + MIN_SAMPLES_SPLIT: config.get(MIN_SAMPLES_SPLIT, [2, 5, 10]),
        # 'classifier__' + MIN_SAMPLES_LEAF: config.get(MIN_SAMPLES_LEAF, [1, 2, 5]),
        # 'classifier__' + MAX_FEATURES: config.get(MAX_FEATURES, ['auto', 'sqrt', 'log2', None]),
        'classifier__' + CRITERION: config.get(CRITERION, ['gini']),
        # 'classifier__' + SPLITTER: config.get(SPLITTER, ['best', 'random']),
        # 'classifier__' + MAX_LEAF_NODES: config.get(MAX_LEAF_NODES, [None, 10, 20, 50]),
        # 'classifier__' + MIN_IMPURITY_DECREASE: config.get(MIN_IMPURITY_DECREASE, [0.0, 0.01, 0.1]),
    }


class DecisionTreeModelBuilderBuilder(BaseModelBuilder):

    def __init__(self, config: Dict):
        super().__init__(config)
        self.bin_edges = dict()
        self.columns = list()
        self.binned_columns = [PRICE_PCT_CHANGE, BUY_VOLUME_PCT_CHANGE,
                               SELL_VOLUME_PCT_CHANGE, TOTAL_VOLUME_PCT_CHANGE,
                               PERCENTAGE_OF_1_MILLION_MARKET_CAP,
                               PRICE_COLUMN, CHANGE_FROM_ATL,
                               CHANGE_FROM_ATH, CUMULATIVE_VOLUME,
                               AGE_IN_MINUTES_COLUMN, TOTAL_VOLUME_COLUMN]
        self.model = None

    def get_columns(self):
        return self.columns

    def get_model(self):
        return self.model

    def build_model(self):
        self.model = DecisionTreeClassifier(random_state=RANDOM_SEED)

    def prepare_dataset(self, data: pd.DataFrame, sorted_data: bool) -> pd.DataFrame:

        logger.info("Remove unused columns from data")
        if sorted_data:
            data = data.sort_values(by=["token", "trading_minute"]).reset_index(drop=True)
        else:
            data = data.sample(frac=1, random_state=RANDOM_SEED).reset_index(drop=True)

        remove_columns_dataframe(data, self.non_training_columns)

        return data

    def prepare_prediction_data(self, data: pd.DataFrame, validation: bool) -> Tuple[pd.DataFrame, List[bool]]:
        logger.info("Remove unused columns")
        data = remove_columns_dataframe(data, self.non_training_columns)
        data.drop(columns=[TOKEN_COlUMN], inplace=True)

        logger.info("Bin data")
        data = bin_data(data, self.binned_columns, self.bin_edges)

        if validation:
            data_x = data[self.columns]
            data_y = data[LABEL_COLUMN]
            return data_x, data_y

        return data, []

    def train(self, train_data: pd.DataFrame, val_data: pd.DataFrame):
        logger.info("Tune hyperparameters")
        param_grid = get_tree_hyperparameters(self.config)
        best_model = train_loop(train_data.copy(), self.config, self.binned_columns, self.model, param_grid)

        logger.info("Train model on full test set")
        self.columns = best_model["selected_columns"]
        train_data = create_sliding_window_flat(train_data, step_size=best_model[STEP_SIZE_KEY])
        train_data.drop(columns=[TOKEN_COlUMN], inplace=True)
        self.bin_edges = compute_bin_edges(train_data, self.binned_columns,
                                           best_model['data_preprocess__' + BIN_AMOUNT_KEY])
        train_data = bin_data(train_data, self.binned_columns, self.bin_edges)
        train_x = train_data[self.columns]
        train_y = train_data[LABEL_COLUMN]
        classifier_params = {k.replace('classifier__', ''): v for k, v in best_model.items() if
                             k.startswith('classifier__')}

        self.model = DecisionTreeClassifier(random_state=RANDOM_SEED, **classifier_params)
        self.model.fit(train_x, train_y)

        logger.info("Validate final model")
        val_x, val_y = self.prepare_prediction_data(val_data, True)
        val_predictions = self.model.predict(val_x)

        logger.info("Print evaluation results")
        print_evaluation(val_y, val_predictions)
        run_simulation(val_data, val_y, val_predictions)

    def save(self):
        save_to_pickle((self.model, self.bin_edges, self.columns), os.path.join(MODEL_FOLDER, "simple_tree.pkl"))

    def load_model(self, name):
        self.model, self.bin_edges, self.columns = load_model(name)

    def predict(self, data):
        data = flatten_dataframe_list(data)
        return self.model.predict(data)

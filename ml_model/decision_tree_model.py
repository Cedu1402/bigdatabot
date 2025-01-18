import logging
import os.path
from typing import List, Dict, Tuple, Optional

import pandas as pd
from sklearn.feature_selection import RFE
from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.tree import DecisionTreeClassifier

from constants import BIN_AMOUNT_KEY, PRICE_PCT_CHANGE, BUY_VOLUME_PCT_CHANGE, SELL_VOLUME_PCT_CHANGE, \
    TOTAL_VOLUME_PCT_CHANGE, PERCENTAGE_OF_1_MILLION_MARKET_CAP, RANDOM_SEED, MODEL_FOLDER, PRICE_COLUMN, \
    CHANGE_FROM_ATL, CHANGE_FROM_ATH, CUMULATIVE_VOLUME, AGE_IN_MINUTES_COLUMN, TOTAL_VOLUME_COLUMN, \
    N_FEATURES_TO_SELECT, RFE_STEP_SIZE, CRITERION, TOKEN_COlUMN, STEP_SIZE_KEY, LABEL_COLUMN
from data.data_split import flatten_dataframe_list, get_x_y_of_list
from data.feature_engineering import bin_data, compute_bin_edges
from data.model_data import remove_columns, order_columns, remove_columns_dataframe
from data.pickle_files import save_to_pickle
from data.sliding_window import create_sliding_window_flat
from data_pre_processor.pre_processed_data_loader import LoadPreprocessedDataTransformer
from ml_model.base_model import BaseModelBuilder
from ml_model.load_model import load_model
from ml_model.model_evaluation import print_evaluation

logger = logging.getLogger(__name__)


def get_tree_hyperparameters(config: dict) -> dict:
    return {
        # Dataset and RFE parameters
        'data_preprocess__' + BIN_AMOUNT_KEY: config.get(BIN_AMOUNT_KEY, [300]),
        # 'data_preprocess__' + STEP_SIZE_KEY: config.get(STEP_SIZE_KEY, [1]),
        'rfe__' + N_FEATURES_TO_SELECT: config.get(N_FEATURES_TO_SELECT, [79]),
        'rfe__step': config.get(RFE_STEP_SIZE, [1]),

        # Tree hyperparameters
        # 'classifier__' + MAX_DEPTH: config.get(MAX_DEPTH, [5, 10, 15, None]),
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
        self.config = config
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

    def prepare_dataset(self, data: pd.DataFrame) -> pd.DataFrame:

        logger.info("Remove unused columns from data")
        remove_columns_dataframe(data, self.non_training_columns)

        return data

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

    def train_loop(self, data: pd.DataFrame) -> Dict:
        sliding_window_params = self.config.get(STEP_SIZE_KEY, [1])
        best_hyper_parameters = None
        best_result = None

        for step_size in sliding_window_params:
            logger.info("Define pipeline")

            data = create_sliding_window_flat(data, step_size)
            x_train = data.drop(columns=[LABEL_COLUMN])
            y_train = data[LABEL_COLUMN]

            pipeline = Pipeline([
                ('data_preprocess', LoadPreprocessedDataTransformer(300, self.binned_columns)),  # Preprocessing step
                ('rfe', RFE(self.model, n_features_to_select=75, step=1, verbose=1)),  # Feature selection step
                ('classifier', self.model)  # Estimator step
            ])

            logger.info("Optimize hyperparameters")
            param_grid = get_tree_hyperparameters(self.config)
            x_train.drop(columns=[TOKEN_COlUMN], inplace=True)

            # Set up GridSearchCV with cross-validation
            grid_search = GridSearchCV(pipeline, param_grid, cv=2, verbose=1, scoring='f1')
            grid_search.fit(x_train, y_train)

            if best_result is None or grid_search.best_score_ > best_result:
                best_result = grid_search.best_score_
                best_hyper_parameters = grid_search.best_params_
                rfe_step = grid_search.best_estimator_.named_steps['rfe']
                selected_columns = x_train.columns[rfe_step.support_].tolist()
                best_hyper_parameters["step_size"] = step_size
                best_hyper_parameters["selected_columns"] = selected_columns
                best_hyper_parameters["classifier"] = grid_search.best_estimator_.named_steps['classifier']
                logger.info(f"New best result found: {best_result} with params: {best_hyper_parameters}")

        return best_hyper_parameters

    def train(self, train_data: pd.DataFrame, val_data: pd.DataFrame):
        logger.info("Tune hyperparameters")
        best_model = self.train_loop(train_data.copy())

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
        val_data = bin_data(val_data, self.binned_columns, self.bin_edges)
        val_x = val_data.drop(columns=[LABEL_COLUMN, TOKEN_COlUMN])
        val_x = val_x[self.columns]

        val_y = val_data[LABEL_COLUMN]
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

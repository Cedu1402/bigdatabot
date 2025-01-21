import logging
import os.path
from typing import Dict, Tuple, List

import pandas as pd

from constants import BIN_AMOUNT_KEY, RANDOM_SEED, MODEL_FOLDER, TOKEN_COlUMN, STEP_SIZE_KEY, LABEL_COLUMN, \
    SELL_VOLUME_PCT_CHANGE, PRICE_PCT_CHANGE, BUY_VOLUME_PCT_CHANGE, TOTAL_VOLUME_PCT_CHANGE, \
    PERCENTAGE_OF_1_MILLION_MARKET_CAP, PRICE_COLUMN, CHANGE_FROM_ATL, CHANGE_FROM_ATH, CUMULATIVE_VOLUME, \
    AGE_IN_MINUTES_COLUMN, TOTAL_VOLUME_COLUMN
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


class SKLearnClassifierBuilder(BaseModelBuilder):

    def __init__(self, config: Dict, binned_data: bool, hyper_param_grid: Dict, model_name: str):
        self.binned_data = binned_data
        self.binned_columns = [PRICE_PCT_CHANGE, BUY_VOLUME_PCT_CHANGE,
                               SELL_VOLUME_PCT_CHANGE, TOTAL_VOLUME_PCT_CHANGE,
                               PERCENTAGE_OF_1_MILLION_MARKET_CAP,
                               PRICE_COLUMN, CHANGE_FROM_ATL,
                               CHANGE_FROM_ATH, CUMULATIVE_VOLUME,
                               AGE_IN_MINUTES_COLUMN, TOTAL_VOLUME_COLUMN]
        self.hyper_param_grid = hyper_param_grid
        self.bin_edges = None
        self.model = None
        self.model_name = model_name
        super().__init__(config)

    def get_model(self):
        return self.model

    def build_model(self, config: Dict = None):
        return

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

        if self.binned_data:
            logger.info("Bin data")
            data = bin_data(data, self.binned_columns, self.bin_edges)

        data = data.sort_values(by=['token', 'trading_minute'])
        remove_columns_dataframe(data, self.non_training_columns)
        if validation:
            data_x = data[self.columns]
            data_y = data[LABEL_COLUMN]
            return data_x, data_y
        else:
            data.drop(columns=[TOKEN_COlUMN], inplace=True)

        return data, []

    def train(self, train_data: pd.DataFrame, val_data: pd.DataFrame):
        logger.info("Tune hyperparameters")
        best_model = train_loop(train_data.copy(), self.config, self.binned_columns, self.model, self.hyper_param_grid,
                                self.binned_data)

        logger.info("Train model on full test set")
        self.columns = best_model["selected_columns"]
        train_data = create_sliding_window_flat(train_data, step_size=best_model[STEP_SIZE_KEY])
        train_data.drop(columns=[TOKEN_COlUMN], inplace=True)
        # if self.config.get("balanced", True):
        #     train_data = balance_data(train_data)

        if self.binned_data:
            self.bin_edges = compute_bin_edges(train_data, self.binned_columns,
                                               best_model['data_preprocess__' + BIN_AMOUNT_KEY])
            train_data = bin_data(train_data, self.binned_columns, self.bin_edges)

        train_x = train_data[self.columns]
        train_y = train_data[LABEL_COLUMN]
        classifier_params = {k.replace('classifier__', ''): v for k, v in best_model.items() if
                             k.startswith('classifier__')}

        self.build_model(classifier_params)
        self.model.fit(train_x, train_y)

        logger.info("Validate final model")
        val_x, val_y = self.prepare_prediction_data(val_data.copy(), True)
        val_predictions = self.predict(val_x)

        logger.info("Print evaluation results")
        print_evaluation(val_y, val_predictions)
        run_simulation(val_data, val_y, val_predictions)

    def save(self):
        save_to_pickle((self.model, self.bin_edges, self.columns), os.path.join(MODEL_FOLDER, f"{self.model_name}.pkl"))

    def load_model(self, name):
        self.model, self.bin_edges, self.columns = load_model(name)

    def predict(self, data):
        return self.model.predict(data)

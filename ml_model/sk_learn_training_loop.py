import logging
from typing import Dict, List, Any

import pandas as pd
from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import Pipeline

from constants import STEP_SIZE_KEY, LABEL_COLUMN, TOKEN_COLUMN, TRADING_MINUTE_COLUMN
from data.data_split import balance_data
from data.sliding_window import create_sliding_window_flat
from data_pre_processor.pre_processed_data_loader import LoadPreprocessedDataTransformer

logger = logging.getLogger(__name__)


def train_loop(data: pd.DataFrame, config: Dict, binned_columns: List[str], model: Any, param_grid: Dict,
               binned_data: bool) -> Dict:
    sliding_window_params = config.get(STEP_SIZE_KEY, [1])
    logger.info(sliding_window_params)
    best_hyper_parameters = None
    best_result = None

    for step_size in sliding_window_params:
        logger.info("Define pipeline")

        data = create_sliding_window_flat(data, step_size)
        if config.get("balanced", True):
            data = balance_data(data)

        x_train = data.drop(columns=[LABEL_COLUMN])
        y_train = data[LABEL_COLUMN]
        pipeline_items = []
        if binned_data:
            pipeline_items.append(('data_preprocess', LoadPreprocessedDataTransformer(300, binned_columns)))

        # pipeline_items.append(
        #     ('rfe', RFE(DecisionTreeClassifier(random_state=RANDOM_SEED), n_features_to_select=75, step=1, verbose=1)))
        pipeline_items.append(('classifier', model))
        pipeline = Pipeline(pipeline_items)

        logger.info("Optimize hyperparameters")
        x_train.drop(columns=[TOKEN_COLUMN, TRADING_MINUTE_COLUMN], inplace=True)

        # Set up GridSearchCV with cross-validation
        grid_search = GridSearchCV(pipeline, param_grid, cv=2, verbose=1, scoring='f1', n_jobs=-1)
        grid_search.fit(x_train, y_train)

        if best_result is None or grid_search.best_score_ > best_result:
            best_result = grid_search.best_score_
        best_hyper_parameters = grid_search.best_params_
        # rfe_step = grid_search.best_estimator_.named_steps['rfe']
        # selected_columns = x_train.columns[rfe_step.support_].tolist()
        best_hyper_parameters["step_size"] = step_size
        best_hyper_parameters["selected_columns"] = x_train.columns
        best_hyper_parameters["classifier"] = grid_search.best_estimator_.named_steps['classifier']
        logger.info(f"New best result found: {best_result} with params: {best_hyper_parameters}")

    return best_hyper_parameters

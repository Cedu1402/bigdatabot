import logging
from typing import Dict, List, Any

import pandas as pd
from sklearn.feature_selection import RFE
from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import Pipeline

from constants import STEP_SIZE_KEY, LABEL_COLUMN, TOKEN_COlUMN
from data.sliding_window import create_sliding_window_flat
from data_pre_processor.pre_processed_data_loader import LoadPreprocessedDataTransformer

logger = logging.getLogger(__name__)


def train_loop(data: pd.DataFrame, config: Dict, binned_columns: List[str], model: Any, param_grid: Dict) -> Dict:
    sliding_window_params = config.get(STEP_SIZE_KEY, [1])
    best_hyper_parameters = None
    best_result = None

    for step_size in sliding_window_params:
        logger.info("Define pipeline")

        data = create_sliding_window_flat(data, step_size)
        x_train = data.drop(columns=[LABEL_COLUMN])
        y_train = data[LABEL_COLUMN]

        pipeline = Pipeline([
            ('data_preprocess', LoadPreprocessedDataTransformer(300, binned_columns)),  # Preprocessing step
            ('rfe', RFE(model, n_features_to_select=75, step=1, verbose=1)),  # Feature selection step
            ('classifier', model)  # Estimator step
        ])

        logger.info("Optimize hyperparameters")
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

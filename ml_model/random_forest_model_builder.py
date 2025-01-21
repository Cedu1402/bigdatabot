import logging
from typing import Dict

from sklearn.ensemble import RandomForestClassifier

from constants import BIN_AMOUNT_KEY, RANDOM_SEED, N_FEATURES_TO_SELECT, RFE_STEP_SIZE, CRITERION, MAX_DEPTH, \
    N_ESTIMATORS
from ml_model.sk_learn_classifier_builder import SKLearnClassifierBuilder

logger = logging.getLogger(__name__)


def get_tree_hyperparameters(config: dict) -> dict:
    return {
        # Dataset and RFE parameters
        'data_preprocess__' + BIN_AMOUNT_KEY: config.get(BIN_AMOUNT_KEY, [1000]),
        # 'data_preprocess__' + STEP_SIZE_KEY: config.get(STEP_SIZE_KEY, [1]),
        'rfe__' + N_FEATURES_TO_SELECT: config.get(N_FEATURES_TO_SELECT, [50]),
        'rfe__step': config.get(RFE_STEP_SIZE, [15]),

        # Tree hyperparameters
        # 'classifier__' + MAX_DEPTH: config.get(MAX_DEPTH, [5, 10, 15, None]),
        # 'classifier__' + CRITERION: config.get(CRITERION, ['gini', 'entropy']),
        'classifier__' + N_ESTIMATORS: config.get(CRITERION, [100]),
    }


class RandomForestModelBuilder(SKLearnClassifierBuilder):

    def __init__(self, config: Dict):
        param_grid = get_tree_hyperparameters(config)
        super().__init__(config, True, param_grid, "random_forest")

    def build_model(self, config: Dict = None):
        if config is not None:
            self.model = RandomForestClassifier(class_weight={0: 1, 1: 2}, random_state=RANDOM_SEED, **config)
        else:
            self.model = RandomForestClassifier(class_weight={0: 1, 1: 2}, random_state=RANDOM_SEED)

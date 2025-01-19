import logging
from typing import Dict

from sklearn.tree import DecisionTreeClassifier

from constants import BIN_AMOUNT_KEY, RANDOM_SEED, N_FEATURES_TO_SELECT, RFE_STEP_SIZE, CRITERION, MAX_DEPTH
from ml_model.sk_learn_classifier_builder import SKLearnClassifierBuilder

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


class DecisionTreeModelBuilderBuilder(SKLearnClassifierBuilder):

    def __init__(self, config: Dict):
        param_grid = get_tree_hyperparameters(config)
        super().__init__(config, True, param_grid, "decision_tree")

    def build_model(self, config: Dict = None):
        if config is not None:
            self.model = DecisionTreeClassifier(random_state=RANDOM_SEED, **config)
        else:
            self.model = DecisionTreeClassifier(random_state=RANDOM_SEED)

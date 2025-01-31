import logging
from typing import Dict

from sklearn.ensemble import HistGradientBoostingClassifier

from constants import RANDOM_SEED
from ml_model.sk_learn_classifier_builder import SKLearnClassifierBuilder

logger = logging.getLogger(__name__)


def get_tree_hyperparameters(config: dict) -> dict:
    return {
        # Dataset and RFE parameters
        # 'rfe__' + N_FEATURES_TO_SELECT: config.get(N_FEATURES_TO_SELECT, [122]),
        # 'rfe__step': config.get(RFE_STEP_SIZE, [15]),

        # Tree hyperparameters
        # 'classifier__' + MAX_DEPTH: config.get(MAX_DEPTH, [5, 10, 15, None]),
        # 'classifier__' + CRITERION: config.get(CRITERION, ['gini', 'entropy']),
        # 'classifier__' + N_ESTIMATORS: config.get(CRITERION, [10, 100]),
    }


class HistGradientBoostModelBuilder(SKLearnClassifierBuilder):

    def __init__(self, config: Dict):
        param_grid = get_tree_hyperparameters(config)
        super().__init__(config, False, param_grid, "hist_gradient")

    def build_model(self, config: Dict = None):
        if config is not None:
            self.model = HistGradientBoostingClassifier(random_state=RANDOM_SEED, **config)
        else:
            self.model = HistGradientBoostingClassifier(random_state=RANDOM_SEED)

import logging
from typing import List

from sklearn.base import BaseEstimator, TransformerMixin

from data.feature_engineering import compute_bin_edges, bin_data

logger = logging.getLogger(__name__)


class LoadPreprocessedDataTransformer(BaseEstimator, TransformerMixin):
    def __init__(self, bin_amount: int, binned_columns: List[str]):
        self.bin_amount = bin_amount
        self.binned_columns = binned_columns

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        logger.info(f"Load dataset steps bin_amount {self.bin_amount}")
        bin_edges = compute_bin_edges(X, self.binned_columns, self.bin_amount)
        X = bin_data(X, self.binned_columns, bin_edges)
        return X

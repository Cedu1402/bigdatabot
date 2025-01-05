import logging

import pandas as pd
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix

logger = logging.getLogger(__name__)


def print_evaluation(y, prediction, labels=None):
    """
    Prints evaluation metrics and a labeled confusion matrix.

    Parameters:
    - y: Ground truth labels.
    - prediction: Predicted labels.
    - labels: List of label names (optional). If not provided, inferred from unique values in y.
    """
    accuracy = accuracy_score(y, prediction)
    f1 = f1_score(y, prediction, average='weighted')
    conf_matrix = confusion_matrix(y, prediction)

    # If labels are not provided, infer from the ground truth
    if labels is None:
        labels = sorted(set(y))

    # Create a labeled DataFrame for the confusion matrix
    conf_matrix_df = pd.DataFrame(
        conf_matrix,
        index=[f"True: {label}" for label in labels],
        columns=[f"Pred: {label}" for label in labels]
    )

    logger.info(
        f"Validation Results - Accuracy: {accuracy:.4f}, F1 Score (Weighted): {f1:.4f}"
    )
    logger.info(f"Confusion Matrix:\n{conf_matrix_df.to_string()}")

import logging
from typing import Tuple

import pandas as pd
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix, precision_score

logger = logging.getLogger(__name__)


def print_evaluation(y, prediction, labels=None) -> Tuple[float, float, float]:
    """
    Prints evaluation metrics and a labeled confusion matrix.

    Parameters:
    - y: Ground truth labels.
    - prediction: Predicted labels.
    - labels: List of label names (optional). If not provided, inferred from unique values in y.
    """
    accuracy = accuracy_score(y, prediction)
    precision = precision_score(y, prediction)
    f1 = f1_score(y, prediction)
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

    print(
        f"Validation Results - Precision: {precision:.4f} Accuracy: {accuracy:.4f}, F1 Score: {f1:.4f}"
    )
    print("*" * 50)
    print(f"Confusion Matrix:\n{conf_matrix_df.to_string()}")
    return accuracy, f1, precision

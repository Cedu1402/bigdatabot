from sklearn.metrics import accuracy_score, f1_score

from log import logger


def print_evaluation(y, prediction):
    accuracy = accuracy_score(y, prediction)
    f1 = f1_score(y, prediction, average='weighted')

    logger.info(
        f"Validation Results - Accuracy: {accuracy:.4f}, F1 Score (Weighted): {f1:.4f}"
    )

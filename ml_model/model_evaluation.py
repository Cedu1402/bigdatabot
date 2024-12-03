from sklearn.metrics import accuracy_score, f1_score, confusion_matrix

from structure_log.logger_setup import logger


def print_evaluation(y, prediction):
    accuracy = accuracy_score(y, prediction)
    f1 = f1_score(y, prediction, average='weighted')
    conf_matrix = confusion_matrix(y, prediction)

    logger.info(
        f"Validation Results - Accuracy: {accuracy:.4f}, F1 Score (Weighted): {f1:.4f}"
    )
    logger.info(f"Confusion Matrix:\n{conf_matrix}")

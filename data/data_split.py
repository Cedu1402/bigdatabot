from typing import Tuple, List

import pandas as pd
from sklearn.model_selection import train_test_split


def split_data(data: List[pd.DataFrame], train_ratio: float = 0.7, val_ratio: float = 0.15, test_ratio: float = 0.15) -> \
        Tuple[List[pd.DataFrame], List[pd.DataFrame], List[pd.DataFrame]]:
    """
    Splits the data into training, validation, and test sets.

    Args:
        data: List[DataFrame] containing the data to be split.
        train_ratio: The ratio of data to be used for training.
        val_ratio: The ratio of data to be used for validation.
        test_ratio: The ratio of data to be used for testing.

    Returns:
        A tuple containing (train_data, val_data, test_data).
    """
    if abs(train_ratio + val_ratio + test_ratio - 1) > 1e-6:
        raise ValueError("The sum of train_ratio, val_ratio, and test_ratio must be 1.")

    # Split into train + remaining (val + test)
    train_data, remaining_data = train_test_split(data, train_size=train_ratio, shuffle=True)

    # Split remaining into validation and test
    val_data, test_data = train_test_split(remaining_data, test_size=test_ratio / (val_ratio + test_ratio),
                                           shuffle=True)

    return train_data, val_data, test_data

import random
from typing import Tuple, List

import pandas as pd
from sklearn.model_selection import train_test_split

from constants import LABEL_COLUMN, TOKEN_COlUMN


def flatten_dataframe_list(data: List[pd.DataFrame]) -> pd.DataFrame:
    flat_data = pd.DataFrame()
    for item in data:
        # Append the last row of each DataFrame in the list
        flat_data = pd.concat([flat_data, item.iloc[-1:]], axis=0)
    return flat_data


def get_x_y_of_list(data: List[pd.DataFrame]) -> Tuple[List[pd.DataFrame], List]:
    x_data = list()
    y_data = list()

    for item in data:
        if LABEL_COLUMN in item.columns:
            y = item[LABEL_COLUMN].iloc[0]
            y_data.append(y)

            x = item.drop(columns=[LABEL_COLUMN])
            x_data.append(x)

    return x_data, y_data


def get_x_y_data(train: List[pd.DataFrame], val: List[pd.DataFrame], test: List[pd.DataFrame]) -> (
        Tuple)[List[pd.DataFrame], List, List[pd.DataFrame], List, List[pd.DataFrame], List]:
    x_train, y_train = get_x_y_of_list(train)
    x_val, y_val = get_x_y_of_list(val)
    x_test, y_test = get_x_y_of_list(test)

    return x_train, y_train, x_val, y_val, x_test, y_test


def balance_data(data: List[pd.DataFrame]) -> List[pd.DataFrame]:
    true_data = [item for item in data if item[LABEL_COLUMN].iloc[0]]
    false_data = [item for item in data if not item[LABEL_COLUMN].iloc[0]]

    fair_amount = len(true_data) if len(true_data) < len(false_data) else len(false_data)

    result = random.sample(false_data, fair_amount)
    result.extend(random.sample(true_data, fair_amount))

    return result


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

    tokens = {df[TOKEN_COlUMN].iloc[0] for df in data}

    # Split into train + remaining (val + test)
    train_tokens, remaining_tokens = train_test_split(list(tokens), train_size=train_ratio, shuffle=True)

    # Split remaining into validation and test
    if test_ratio > 0:
        val_tokens, test_tokens = train_test_split(remaining_tokens,
                                                   test_size=test_ratio / (val_ratio + test_ratio),
                                                   shuffle=True)
    else:
        val_tokens = remaining_tokens
        test_tokens = []

    train_data = [df for df in data if df[TOKEN_COlUMN].iloc[0] in train_tokens]
    val_data = [df for df in data if df[TOKEN_COlUMN].iloc[0] in val_tokens]
    test_data = [df for df in data if df[TOKEN_COlUMN].iloc[0] in test_tokens]

    return train_data, val_data, test_data

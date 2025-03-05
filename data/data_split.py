from datetime import datetime
from typing import Tuple, List, Dict

import pandas as pd

from constants import LABEL_COLUMN, TOKEN_COLUMN, TRADING_MINUTE_COLUMN, PRICE_COLUMN


def get_index_of_similar_price(token_price_data, current_price):
    return token_price_data[token_price_data['age'] < 300].groupby(TOKEN_COLUMN, group_keys=False).apply(
        lambda group: (group[PRICE_COLUMN] - current_price).abs().idxmin()
    )


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


def balance_data(data: pd.DataFrame) -> pd.DataFrame:
    # Get the number of samples in the minority class
    minority_count = data[LABEL_COLUMN].value_counts().min()

    # Drop excess rows from the majority class
    data = data.groupby(LABEL_COLUMN).apply(lambda x: x.sample(minority_count)).reset_index(drop=True)

    return data


def get_split_dates(split_1: float, split_2: float, start_time: datetime, end_time: datetime) -> Tuple[
    datetime, datetime]:
    total_duration = end_time - start_time
    first_split_time = start_time + total_duration * split_1
    second_split_time = start_time + total_duration * split_2

    return first_split_time, second_split_time


def get_start_end_time(data: pd.DataFrame) -> Tuple[datetime, datetime]:
    start_time = data[TRADING_MINUTE_COLUMN].min()
    end_time = data[TRADING_MINUTE_COLUMN].max()
    return start_time, end_time


def get_token_splits(token_data: Dict[str, datetime], first_split_time: datetime, second_split_time: datetime) -> Tuple[
    List[str], List[str], List[str]]:
    test_set_tokens = [key for key, value in token_data.items() if value <= first_split_time]

    validation_set_tokens = [key for key, value in token_data.items() if
                             second_split_time >= value > first_split_time]

    train_set_tokens = [key for key, value in token_data.items() if value >= second_split_time]

    return test_set_tokens, validation_set_tokens, train_set_tokens


def get_token_filtered_set(data: pd.DataFrame, tokens: List[str]) -> pd.DataFrame:
    return data[data[TOKEN_COLUMN].isin(tokens)]


def split_data(data: pd.DataFrame, token_data: Dict[str, datetime]) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    start_time, end_time = get_start_end_time(data)
    first_split_time, second_split_time = get_split_dates(0.1, 0.2, start_time, end_time)
    test_set_tokens, validation_set_tokens, train_set_tokens = get_token_splits(token_data, first_split_time,
                                                                                second_split_time)

    test_set = get_token_filtered_set(data, test_set_tokens)
    validation_set = get_token_filtered_set(data, validation_set_tokens)
    train_set = get_token_filtered_set(data, train_set_tokens)

    return train_set, validation_set, test_set

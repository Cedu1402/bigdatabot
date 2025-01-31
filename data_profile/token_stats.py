from typing import List

import pandas as pd

from constants import TOKEN_COlUMN, LABEL_COLUMN


def get_tokens(data: pd.DataFrame) -> List[str]:
    return data[TOKEN_COlUMN].unique().tolist()


def get_good_tokens(data: pd.DataFrame) -> List[str]:
    good_data = data[data[LABEL_COLUMN] == True]
    good_tokens = good_data[TOKEN_COlUMN].unique().tolist()
    return good_tokens


def print_token_stats(data: pd.DataFrame, set_name: str = "Test"):
    tokens = get_tokens(data)
    good_tokens = get_good_tokens(data)

    print("*" * 75)
    print(f"Token stats for {set_name}")
    print(f"Total tokens: {len(tokens)}")
    print(f"Good tokens: {len(good_tokens)}")

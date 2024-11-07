from typing import List

import pandas as pd


def remove_columns(data: List[pd.DataFrame], columns: List[str]) -> List[pd.DataFrame]:
    for item in data:
        item.drop(columns=columns, inplace=True, errors='ignore')  # Avoid errors if columns are missing
    return data

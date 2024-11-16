from typing import List

import pandas as pd


def remove_columns(data: List[pd.DataFrame], columns: List[str]) -> List[pd.DataFrame]:
    for item in data:
        item.drop(columns=columns, inplace=True, errors='ignore')  # Avoid errors if columns are missing
    return data


def order_columns(data: List[pd.DataFrame], columns: List[str]) -> List[pd.DataFrame]:
    new_data = list()
    for item in data:
        new_item = pd.DataFrame(columns)
        for col in columns:
            try:
                new_item[col] = item[col]
            except Exception as e:
                print("why?", col)

        new_data.append(new_item)
    return new_data

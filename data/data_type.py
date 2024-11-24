import pandas as pd

from constants import PRICE_COLUMN, BUY_VOLUME_COLUMN, SELL_VOLUME_COLUMN


def convert_columns(data: pd.DataFrame) -> pd.DataFrame:
    data.loc[:, PRICE_COLUMN] = pd.to_numeric(data[PRICE_COLUMN], errors='coerce')
    data.loc[:, BUY_VOLUME_COLUMN] = pd.to_numeric(data[BUY_VOLUME_COLUMN], errors='coerce')
    data.loc[:, SELL_VOLUME_COLUMN] = pd.to_numeric(data[SELL_VOLUME_COLUMN], errors='coerce')
    return data


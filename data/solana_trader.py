import pandas as pd


def get_trader_from_trades(trade_list: pd.DataFrame) -> pd.DataFrame:
    unique_values = trade_list['trader_id'].unique()
    traders = pd.DataFrame(unique_values, columns=['trader'])
    return traders
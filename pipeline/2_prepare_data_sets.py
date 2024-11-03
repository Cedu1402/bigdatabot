from typing import Tuple

import pandas as pd
from dotenv import load_dotenv

from data.solana_trader import get_trader_from_trades
from dune.data_collection import collect_all_data


def prepare_data_set(use_cache: bool):
     volume_close_1m, top_trader_trades = collect_all_data(use_cache)

     # Get traders
     traders = get_trader_from_trades(top_trader_trades)

     # Finish volume data if tokens had no tx in some minutes
    
     # Add trader info to volume data

     # Split volume data into sliding window chunks of 10min

     # Add labels for trading info (good buy or not)

     # Split into train/validation/test set

     pass


if __name__ == '__main__':
    load_dotenv()
    use_cached_data = True
    prepare_data_set(use_cached_data)

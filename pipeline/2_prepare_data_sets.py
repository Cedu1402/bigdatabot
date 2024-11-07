from dotenv import load_dotenv

from constants import DRAW_DOWN_PERCENTAGE, WIN_PERCENTAGE
from data.close_volume_data import add_missing_minutes
from data.combine_price_trades import add_trader_info_to_price_data
from data.label_data import label_data
from data.sliding_window import create_sliding_windows
from data.solana_trader import get_trader_from_trades
from dune.data_collection import collect_all_data


def prepare_data_set(use_cache: bool):
    volume_close_1m, top_trader_trades = collect_all_data(use_cache)

    # Get traders
    traders = get_trader_from_trades(top_trader_trades)

    # Finish volume data if tokens had no tx in some minutes
    volume_close_1m = add_missing_minutes(volume_close_1m)

    # Add trader info to volume data
    full_data = add_trader_info_to_price_data(volume_close_1m, traders, top_trader_trades)

    # Split volume data into sliding window chunks of 10min
    split_data = create_sliding_windows(full_data)

    # Add labels for trading info (good buy or not)
    labeled_data = label_data(split_data, volume_close_1m, WIN_PERCENTAGE, DRAW_DOWN_PERCENTAGE)

    # Split into train/validation/test set

    pass


if __name__ == '__main__':
    load_dotenv()
    use_cached_data = True
    prepare_data_set(use_cached_data)

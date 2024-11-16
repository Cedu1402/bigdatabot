import os
from typing import List

import pandas as pd

from constants import WIN_PERCENTAGE, DRAW_DOWN_PERCENTAGE, CACHE_FOLDER, TRAIN_VAL_TEST_FILE, VALIDATION_FILE
from data.close_volume_data import add_missing_minutes
from data.combine_price_trades import add_trader_info_to_price_data
from data.data_split import balance_data, split_data
from data.data_type import convert_columns
from data.feature_engineering import add_features
from data.label_data import label_data
from data.pickle_files import save_to_pickle, load_from_pickle
from data.sliding_window import create_sliding_windows
from data.solana_trader import get_trader_from_trades
from dune.data_collection import collect_all_data, collect_validation_data
from log import logger


def prepare_steps(top_trader_trades: pd.DataFrame, volume_close_1m: pd.DataFrame) -> List[pd.DataFrame]:
    # Get traders
    traders = get_trader_from_trades(top_trader_trades)

    # Finish volume data if tokens had no tx in some minutes
    volume_close_1m = add_missing_minutes(volume_close_1m)

    # Add trader info to volume data
    full_data = add_trader_info_to_price_data(volume_close_1m, traders, top_trader_trades)

    full_data = convert_columns(full_data)

    # Add features
    full_data = add_features(full_data)

    # Split volume data into sliding window chunks of 10min
    full_data_windows = create_sliding_windows(full_data)

    # Add labels for trading info (good buy or not)
    labeled_data = label_data(full_data_windows, volume_close_1m, WIN_PERCENTAGE, DRAW_DOWN_PERCENTAGE)

    return labeled_data


def add_inactive_traders(top_trader_trades: pd.DataFrame, columns: List[str], labeled_data: List[pd.DataFrame]) -> List[
    pd.DataFrame]:
    current_traders = get_trader_from_trades(top_trader_trades)
    for col in columns:
        if "_state" in col:
            trader = col.replace("_state", "").replace("trader_", "")
            if trader not in current_traders:
                for data in labeled_data:
                    data["trader_" + trader + "_state"] = 0

    return labeled_data


def prepare_validation_data(use_cache: bool, columns: List[str]):
    if use_cache and os.path.exists(os.path.join(CACHE_FOLDER, VALIDATION_FILE + ".pkl")):
        logger.info("Load validation data from cache")
        return load_from_pickle(os.path.join(CACHE_FOLDER, VALIDATION_FILE + ".pkl"))

    logger.info("Load volume/price data from dune")
    volume_close_1m, top_trader_trades = collect_validation_data(use_cache)
    logger.info("Prepare validation data")
    labeled_data = prepare_steps(top_trader_trades, volume_close_1m)
    logger.info("Add inactive traders")
    labeled_data = add_inactive_traders(top_trader_trades, columns, labeled_data)
    logger.info("Cache prepared data")
    save_to_pickle(labeled_data, os.path.join(CACHE_FOLDER, VALIDATION_FILE + ".pkl"))
    return labeled_data


def prepare_dataset(use_cache: bool):
    if use_cache and os.path.exists(os.path.join(CACHE_FOLDER, TRAIN_VAL_TEST_FILE + ".pkl")):
        return load_from_pickle(os.path.join(CACHE_FOLDER, TRAIN_VAL_TEST_FILE + ".pkl"))
    logger.info("Load volume/price data from dune")
    volume_close_1m, top_trader_trades = collect_all_data(use_cache)
    logger.info("Prepare data")
    labeled_data = prepare_steps(top_trader_trades, volume_close_1m)
    logger.info("Split data into train, val, test")
    # Split into train/validation/test set
    train, val, test = split_data(labeled_data)

    # Balance data into 50% true / 50% false samples
    logger.info("Balance train set")
    train = balance_data(train)
    logger.info("Save data to cache")
    save_to_pickle((train, val, test), os.path.join(CACHE_FOLDER, TRAIN_VAL_TEST_FILE + ".pkl"))

    return train, val, test

from typing import List

import pandas as pd

from constants import TRAIN_VAL_TEST_FILE, VALIDATION_FILE, LABEL_COLUMN
from data.cache_data import read_cache_data_with_config, save_cache_data_with_config
from data.close_volume_data import add_missing_minutes
from data.combine_price_trades import add_trader_info_to_price_data
from data.data_split import balance_data, split_data
from data.data_type import convert_columns
from data.feature_engineering import add_features
from data.label_data import label_dataset
from data.sliding_window import create_sliding_windows
from data.solana_trader import get_trader_from_trades
from dune.data_collection import collect_all_data, collect_validation_data
from log import logger


def prepare_steps(top_trader_trades: pd.DataFrame, volume_close_1m: pd.DataFrame, config: dict) -> pd.DataFrame:
    # Get traders
    logger.info("Get trader")
    traders = get_trader_from_trades(top_trader_trades)
    logger.info("Fill missing data")
    # Finish volume data if tokens had no tx in some minutes
    volume_close_1m = add_missing_minutes(volume_close_1m)
    logger.info("Add trader labels")
    # Add trader info to volume data
    full_data = add_trader_info_to_price_data(volume_close_1m, traders, top_trader_trades)
    logger.info("Adjust type of columns")
    full_data = convert_columns(full_data)
    # Add features
    logger.info("Add features")
    full_data = add_features(full_data)
    logger.info("Add labels")
    # Add labels for trading info (good buy or not)
    labeled_data = label_dataset(full_data,
                                 config["win_percentage"],
                                 config["draw_down_percentage"],
                                 config["max_trading_time"])

    return labeled_data


def add_inactive_traders(existing_traders: List[str], columns: List[str],
                         labeled_data: pd.DataFrame) -> pd.DataFrame:
    for col in columns:
        if "_state" in col:
            trader = col.replace("_state", "").replace("trader_", "")
            if trader not in existing_traders:
                labeled_data["trader_" + trader + "_state"] = 0

    return labeled_data


def prepare_validation_data(use_cache: bool, columns: List[str], config: dict):
    cache_data = read_cache_data_with_config(VALIDATION_FILE, config) if use_cache else None
    if use_cache and cache_data is not None:
        return cache_data

    logger.info("Load volume/price data from dune")
    volume_close_1m, top_trader_trades = collect_validation_data(use_cache)
    logger.info("Prepare validation data")
    labeled_data = prepare_steps(top_trader_trades, volume_close_1m, config)
    logger.info("Add inactive traders")
    current_traders = get_trader_from_trades(top_trader_trades)
    labeled_data = add_inactive_traders(current_traders["trader"].to_list(), columns, labeled_data)
    logger.info("Split into windows")
    # Split volume data into sliding window chunks of 10min
    full_data_windows = create_sliding_windows(labeled_data, config["window_size"], config["step_size"])

    logger.info("Cache prepared data")
    save_cache_data_with_config(VALIDATION_FILE, config, full_data_windows)
    return full_data_windows


def log_class_distribution(train, val, test, class_column='label'):
    """
    Logs the distribution of binary classes in each dataset (train, validation, test).

    Parameters:
    - train: The training dataset
    - val: The validation dataset
    - test: The test dataset
    - class_column: The name of the column containing the class labels (default is 'label')
    """

    # Helper function to log class distribution
    def class_distribution(dataset, name):
        distribution = len([0 for item in dataset if item[LABEL_COLUMN].iloc[0]]) / (len(dataset) / 100)
        logger.info(f"{name} set class distribution:")
        logger.info(f"\n{distribution}\n")  # Log the distribution with a blank line for readability

    # Log class distribution for each set
    class_distribution(train, 'Train')
    class_distribution(val, 'Validation')
    class_distribution(test, 'Test')


def prepare_dataset(use_cache: bool, config: dict):
    cache_data = read_cache_data_with_config(TRAIN_VAL_TEST_FILE, config) if use_cache else None
    if use_cache and cache_data is not None:
        return cache_data

    logger.info("Load volume/price data from dune")
    volume_close_1m, top_trader_trades = collect_all_data(use_cache)
    logger.info("Prepare data")
    labeled_data = prepare_steps(top_trader_trades, volume_close_1m, config)
    logger.info("Split into windows")
    # Split volume data into sliding window chunks of 10min
    labeled_data = create_sliding_windows(labeled_data, config["window_size"], config["step_size"])

    logger.info("Split data into train, val, test")
    # Split into train/validation/test set
    train, val, test = split_data(labeled_data)
    log_class_distribution(train, val, test, LABEL_COLUMN)
    # Balance data into 50% true / 50% false samples
    logger.info("Balance train set")
    train = balance_data(train)

    logger.info("Save data to cache")
    save_cache_data_with_config(TRAIN_VAL_TEST_FILE, config, (train, val, test))

    return train, val, test

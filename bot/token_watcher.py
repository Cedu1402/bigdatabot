import copy
import logging
from asyncio import sleep
from datetime import datetime
from typing import List, Optional

import pandas as pd
from dotenv import load_dotenv
from rq import Queue

from birdeye_api.ohlcv_endpoint import get_time_frame_ohlcv
from bot.trade_watcher import watch_trade
from constants import BIN_AMOUNT_KEY, TRADE_QUEUE
from data.close_volume_data import get_trading_minute
from data.data_type import convert_columns
from data.dataset import add_inactive_traders
from data.feature_engineering import add_features
from data.redis_helper import get_sync_redis
from data.trade_data import get_valid_trades, add_trader_actions_to_dataframe, get_traders
from database.token_creation_info_table import select_token_creation_info
from database.token_dataset_table import insert_token_dataset
from database.token_watch_table import get_token_watch, set_end_time, insert_token_watch
from database.trade_table import get_trades_by_token
from dto.token_dataset_model import TokenDataset
from dto.trade_model import Trade
from ml_model.decision_tree_model import DecisionTreeModelBuilderBuilder
from structure_log.logger_setup import setup_logger, ensure_logging_flushed

setup_logger("token_watcher")
logger = logging.getLogger(__name__)


def get_valid_trades_of_token(token: str, trading_minute: datetime) -> List[Trade]:
    trades = get_trades_by_token(token)
    valid_trades = get_valid_trades(trades, trading_minute)

    return valid_trades


async def get_base_data(valid_trades: List[Trade], trading_minute: datetime, token: str) -> Optional[pd.DataFrame]:
    df = add_trader_actions_to_dataframe(valid_trades, trading_minute)
    # get close and volume data
    price_df = await get_time_frame_ohlcv(token, trading_minute, 11, "1m")
    if price_df is None:
        return None

    df = pd.merge(
        df,
        price_df,
        left_index=True,  # Join on the index of df
        right_index=True,  # Join on the index of price_df
        how="inner"  # Keeps only the rows with matching indices in both DataFrames
    )
    return df


def check_if_token_done(token: str) -> bool:
    try:
        token_watch_info = get_token_watch(token)
        if token_watch_info is not None and token_watch_info[3]:
            logger.info("Token done", extra={"token": str(token)})
            return True
    except Exception as e:
        logger.exception("Failed to check if token is done.")
        return True

    return False


def check_age_of_token(token: str) -> bool:
    logger.info("Check trading minute", extra={"token": str(token)})
    token_create_info = select_token_creation_info(token)
    if token_create_info is None:
        logger.error("Failed to get token", extra={"token": str(token)})
        return False

    token_create_time, owner = token_create_info

    # check if coin is older than 4h if yes exit
    if (datetime.utcnow() - token_create_time).total_seconds() > 120 * 60:
        logger.info("Stop watch for token because of age", extra={"token": str(token)})
        return False

    logger.info("Token still in valid time range", extra={"token": str(token)})
    return True


async def prepare_current_dataset(valid_trades: List[Trade], trading_minute: datetime, token: str,
                                  columns: List[str]) -> Optional[pd.DataFrame]:
    logger.info("Get base dataset")
    df = await get_base_data(valid_trades, trading_minute, token)
    if df is None:
        return None

    # run data preparation
    logger.info("Adjust type of columns", extra={"token": str(token), "trading_minute": trading_minute})
    df = convert_columns(df)

    # Add features
    logger.info("Add features", extra={"token": str(token), "trading_minute": trading_minute})
    df = add_features(df)

    logger.info("Add inactive traders", extra={"token": str(token), "trading_minute": trading_minute})
    df = add_inactive_traders(get_traders(valid_trades), columns, df)

    return df


async def watch_token(token) -> bool:
    # every minute check if we should buy
    load_dotenv()
    logger.info("Start token watch", extra={"token": str(token)})
    logger.info("Check if token already watched", extra={"token": str(token)})

    if check_if_token_done(token):
        return False

    logger.info("Mark token for watch", extra={"token": str(token)})
    insert_token_watch(token, datetime.utcnow(), None)

    queue = Queue(TRADE_QUEUE, connection=get_sync_redis(), default_timeout=9000)

    try:
        logger.info("Load model")
        config = dict()
        config[BIN_AMOUNT_KEY] = 10
        model = DecisionTreeModelBuilderBuilder(config)
        model.load_model("simple_tree")
        last_trading_minute = None
        while True:
            try:
                trading_minute = get_trading_minute()
                if not check_age_of_token(token):
                    logger.info("Token watch finished because of age", extra={"token": str(token)})
                    return False

                if last_trading_minute is not None and (trading_minute - last_trading_minute).total_seconds() == 0:
                    logger.info("Skip because not yet next trading minute",
                                extra={"token": str(token),
                                       "trading_minute": trading_minute,
                                       "last_trading_minute": last_trading_minute})
                    await sleep(5)
                    continue

                last_trading_minute = copy.deepcopy(trading_minute)

                # get trades and prepare trader columns
                logger.info("Get valid trades", extra={"token": str(token)})
                valid_trades = get_valid_trades_of_token(token, trading_minute)
                if len(valid_trades) == 0:
                    logger.info("No valid trades", extra={"token": str(token), "trading_minute": trading_minute})
                    await sleep(5)
                    continue

                logger.info("Prepare dataset for prediction", extra={"token": str(token)})
                df = await prepare_current_dataset(valid_trades, trading_minute, token, model.get_columns())
                if df is None:
                    logger.error("Issue in creating dataset",
                                 extra={'token': token, 'trading_minute': trading_minute})
                    await sleep(30)
                    continue

                insert_token_dataset(TokenDataset(token, trading_minute, df))

                # predict
                logger.info("Prepare data for model prediction", extra={"token": str(token)})
                prediction_data, _ = model.prepare_prediction_data(copy.deepcopy([df]), False)
                logger.info("Make prediction for tradeing minute")
                prediction = model.predict(prediction_data)
                logger.info("Prediction for trading minute done")

                # start trading task and exit
                if prediction[0]:
                    logger.info("Start trader watcher", extra={"token": str(token), "trading_minute": trading_minute})
                    queue.enqueue(watch_trade, token)
                    logger.info("Added trade watcher", extra={"token": str(token)})
                    return True
                else:
                    logger.info("No buy signal found by model", extra={"token": str(token)})
                    await sleep(5)
            except Exception as e:
                logger.exception("Failed to predict buy signal", exc_info=True, extra={"token": str(token)})
                await sleep(5)
                continue
    except Exception as e:
        logger.exception("Failed to get token", extra={"token": str(token)}, exc_info=True)
    finally:
        set_end_time(token, datetime.utcnow())
        ensure_logging_flushed()

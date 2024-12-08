import copy
import json
import logging
from asyncio import sleep
from datetime import datetime
from typing import List

import pandas as pd
import redis
from dotenv import load_dotenv
from rq import Queue

from birdeye_api.ohlcv_endpoint import get_time_frame_ohlcv
from bot.trade_watcher import watch_trade
from constants import CREATE_PREFIX, TRADE_PREFIX, BIN_AMOUNT_KEY, TRADE_QUEUE, CURRENT_TOKEN_WATCH_KEY
from data.close_volume_data import get_trading_minute
from data.data_format import get_sol_price, transform_price_to_tokens_per_sol
from data.data_type import convert_columns
from data.dataset import add_inactive_traders
from data.feature_engineering import add_features
from data.redis_helper import get_async_redis, decrement_counter, get_sync_redis
from data.trade_data import get_valid_trades, add_trader_actions_to_dataframe, get_traders
from ml_model.decision_tree_model import DecisionTreeModel
from solana_api.trade_model import Trade
from structure_log.logger_setup import setup_logger, ensure_logging_flushed

setup_logger("token_watcher")
logger = logging.getLogger(__name__)


async def get_valid_trades_of_token(token: str, r: redis.Redis, trading_minute: datetime) -> List[Trade]:
    trades = await r.lrange(TRADE_PREFIX + token, 0, -1)
    trades = [Trade(**json.loads(item)) for item in trades]
    valid_trades = get_valid_trades(trades, trading_minute)

    return valid_trades


async def get_base_data(valid_trades: List[Trade], trading_minute: datetime, token: str) -> pd.DataFrame:
    df = add_trader_actions_to_dataframe(valid_trades, trading_minute)
    # get close and volume data
    price_df = await get_time_frame_ohlcv(token, trading_minute, 11, "1m")

    df = pd.merge(
        df,
        price_df,
        left_index=True,  # Join on the index of df
        right_index=True,  # Join on the index of price_df
        how="inner"  # Keeps only the rows with matching indices in both DataFrames
    )
    return df


async def check_if_token_done(token: str, r: redis.asyncio.Redis) -> bool:
    try:
        token_done = await r.get(token + "_done")
        if token_done is not None:
            logger.info("Token done", extra={"token": str(token)})
            return True
    except Exception as e:
        logger.exception("Failed to check if token is done.")
        return True

    return False


async def check_age_of_token(r: redis.asyncio.Redis, token: str) -> bool:
    logger.info("Check trading minute", extra={"token": str(token)})

    create_info = await r.get(CREATE_PREFIX + token)
    token_create_time, owner = json.loads(create_info)
    token_create_time = datetime.fromisoformat(token_create_time)

    # check if coin is older than 4h if yes exit
    if (datetime.utcnow() - token_create_time).total_seconds() > 120 * 60:
        logger.info("Stop watch for token because of age", extra={"token": str(token)})
        return False

    logger.info("Token still in valid time range", extra={"token": str(token)})
    return True


async def prepare_current_dataset(valid_trades: List[Trade], trading_minute: datetime, token: str,
                                  columns: List[str], r: redis.asyncio.Redis) -> pd.DataFrame:
    logger.info("Get base dataset")
    df = await get_base_data(valid_trades, trading_minute, token)

    # run data preparation
    logger.info("Adjust type of columns", extra={"token": str(token), "trading_minute": trading_minute})
    df = convert_columns(df)

    # transform to sol price
    logger.info("Adjust prices based on current sol price")
    solana_price = await get_sol_price(r)
    df = transform_price_to_tokens_per_sol(df, solana_price)

    # Add features
    logger.info("Add features", extra={"token": str(token), "trading_minute": trading_minute})
    df = add_features(df, has_total_volume=True)

    logger.info("Add inactive traders", extra={"token": str(token), "trading_minute": trading_minute})
    df = add_inactive_traders(get_traders(valid_trades), columns, df)

    return df


async def watch_token(token) -> bool:
    # every minute check if we should buy
    load_dotenv()
    logger.info("Start token watch", extra={"token": str(token)})
    r = get_async_redis()

    logger.info("Check if token already traded", extra={"token": str(token)})
    if await check_if_token_done(token, r):
        return False

    queue = Queue(TRADE_QUEUE, connection=get_sync_redis(), default_timeout=9000)
    await r.incr(CURRENT_TOKEN_WATCH_KEY)

    try:
        logger.info("Load model")
        config = dict()
        config[BIN_AMOUNT_KEY] = 10
        model = DecisionTreeModel(config)
        model.load_model("simple_tree")
        last_trading_minute = None
        while True:
            try:
                trading_minute = get_trading_minute()
                if not await check_age_of_token(r, token):
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
                valid_trades = await get_valid_trades_of_token(token, r, trading_minute)
                if len(valid_trades) == 0:
                    logger.info("No valid trades", extra={"token": str(token), "trading_minute": trading_minute})
                    await sleep(5)
                    continue

                logger.info("Prepare dataset for prediction", extra={"token": str(token)})
                df = await prepare_current_dataset(valid_trades, trading_minute, token, model.get_columns(), r)

                # predict
                logger.info("Prepare data for model prediction", extra={"token": str(token)})
                prediction_data, _ = model.prepare_prediction_data(copy.deepcopy([df]), False)
                prediction = model.predict(prediction_data)

                # start trading task and exit
                if prediction[0]:
                    logger.info("Start trader watcher", extra={"token": str(token), "trading_minute": trading_minute})
                    queue.enqueue(watch_trade, token)
                    await r.set(token + "_done", str(True))
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
        await decrement_counter(CURRENT_TOKEN_WATCH_KEY, r)
        ensure_logging_flushed()

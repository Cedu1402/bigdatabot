import asyncio
import copy
import random
from datetime import datetime
from typing import Optional

from dotenv import load_dotenv

from bot.token_watcher import prepare_current_dataset
from config.config_reader import load_yaml_to_dict
from constants import BIN_AMOUNT_KEY, CONFIG_2_FILE, TOKEN_COlUMN, RANDOM_SEED, TRADING_MINUTE_COLUMN
from data.combine_price_trades import prepare_timestamps, convert_trading_amount
from data.dataset import prepare_test_data, prepare_dataset
from database.token_dataset_table import get_token_datasets_by_token
from dune.data_collection import collect_all_data
from ml_model.hist_gradient_model_builder import HistGradientBoostModelBuilder


async def data_leak_check(amount_of_tokens: int = 10, use_cache: bool = True):
    # load validation data
    data_config = load_yaml_to_dict(CONFIG_2_FILE)
    _, val, _ = await prepare_dataset(use_cache, data_config)
    volume_close_1m, top_trader_trades = await collect_all_data(use_cache)
    volume_close_1m, top_trader_trades = prepare_timestamps(volume_close_1m, top_trader_trades)
    top_trader_trades = convert_trading_amount(top_trader_trades)

    # # select x random tokens
    tokens = val[TOKEN_COlUMN].unique().tolist()
    random.seed = RANDOM_SEED
    selected_tokens = random.sample(tokens, amount_of_tokens)

    model_builder = HistGradientBoostModelBuilder(dict())
    model_builder.load_model("hist_gradient")

    # predict token on full data
    val = val[val[TOKEN_COlUMN].isin(selected_tokens)]
    val_x, val_y = model_builder.prepare_prediction_data(val.copy(), True)
    val_predictions = model_builder.predict(val_x)

    # predict token on split data using same logic to create df like production
    for token in selected_tokens:
        test = val[val[TOKEN_COlUMN] == token]
        starting_minute = val[val[TOKEN_COlUMN] == token][TRADING_MINUTE_COLUMN].min()
        end_minute = val[val[TOKEN_COlUMN] == token][TRADING_MINUTE_COLUMN].max()
        current_minute = starting_minute

        while current_minute <= end_minute:
            valid_trades = top_trader_trades[
                (top_trader_trades[TOKEN_COlUMN] == token) & (top_trader_trades[TRADING_MINUTE_COLUMN] <= starting_minute)]

            df = await prepare_current_dataset(valid_trades, starting_minute, token, model_builder.get_columns())
            prediction_data, _ = model_builder.prepare_prediction_data(df.copy(), False)
            prediction = model_builder.predict(prediction_data)

            assert prediction == val_predictions[0]  # todo get the correct val_prediction!
            # todo compare the data not only the prediction results.


async def check_token(token: str):
    config = dict()
    config[BIN_AMOUNT_KEY] = 10
    model_builder = HistGradientBoostModelBuilder(dict())
    model_builder.load_model("hist_gradient")
    data_config = load_yaml_to_dict(CONFIG_2_FILE)

    prod_data = get_token_datasets_by_token(token)
    prod_val_x = [item.raw_data for item in prod_data]
    prod_validation_x, _ = model.prepare_prediction_data(copy.deepcopy(prod_val_x), False)
    prod_predictions = model.predict(prod_validation_x)

    # Extract unique trading minutes from prod_val_x
    prod_trading_minutes = list()
    for df in prod_val_x:
        prod_trading_minutes.append(
            df['trading_minute'].iloc[-1].strftime('%Y-%m-%d %H:%M:%S'))  # Standardize to string

    # Filter test_data
    test_data = await prepare_test_data(token, True, model.get_columns(), data_config)
    filtered_test_data = []
    test_list = []
    for df in test_data:
        # Standardize trading_minute to string and check overlap
        trading_minutes = df['trading_minute'].iloc[-1].tz_localize(None).strftime('%Y-%m-%d %H:%M:%S')
        test_list.append(trading_minutes)
        if trading_minutes in prod_trading_minutes:
            filtered_test_data.append(df)

    validation_x, _ = model.prepare_prediction_data(copy.deepcopy(filtered_test_data), False)
    predictions = model.predict(validation_x)

    assert prod_predictions == predictions


def check_time_frame(date_from, date_to):
    pass


async def main(token: Optional[str], date_form: Optional[datetime], date_to: Optional[datetime]):
    if token is not None:
        await check_token(token)
    else:
        check_time_frame(date_form, date_to)


if __name__ == '__main__':
    load_dotenv()
    asyncio.run(data_leak_check())

import asyncio
import copy
from datetime import datetime
from typing import Optional

from dotenv import load_dotenv

from config.config_reader import load_yaml_to_dict
from constants import BIN_AMOUNT_KEY, CONFIG_2_FILE
from data.dataset import prepare_test_data
from database.token_dataset_table import get_token_datasets_by_token
from ml_model.decision_tree_model import DecisionTreeModelBuilderBuilder


def check_token(token: str):
    config = dict()
    config[BIN_AMOUNT_KEY] = 10
    model = DecisionTreeModelBuilderBuilder(config)
    model.load_model("simple_tree")
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
    load_dotenv()
    if token is not None:
        check_token(token)
    else:
        check_time_frame(date_form, date_to)


if __name__ == '__main__':
    asyncio.run(main())

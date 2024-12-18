import asyncio
import copy

from dotenv import load_dotenv

from config.config_reader import load_yaml_to_dict
from constants import BIN_AMOUNT_KEY, CONFIG_2_FILE
from data.dataset import prepare_validation_data
from ml_model.decision_tree_model import DecisionTreeModel
from ml_model.model_evaluation import print_evaluation
import logging
logger = logging.getLogger(__name__)


async def evaluate_model(use_cache: bool):
    config = dict()
    config[BIN_AMOUNT_KEY] = 10
    model = DecisionTreeModel(config)
    model.load_model("simple_tree")
    data_config = load_yaml_to_dict(CONFIG_2_FILE)
    # load current data
    validation_data = await prepare_validation_data(use_cache, model.get_columns(), data_config)
    validation_x, validation_y = model.prepare_prediction_data(copy.deepcopy(validation_data), True)

    # predict
    prediction = model.predict(validation_x)

    # calculate scores
    print_evaluation(validation_y, prediction)

    # calculate return 1 token only one trade
    ape_amount = 50
    total_return = 0
    token_bought = list()
    good_trades = 0
    bad_trades = 0

    for index, data in enumerate(validation_data):
        if not prediction[index]:
            continue

        token = data["token"].iloc[0]
        if token not in token_bought:
            token_bought.append(token)
            if validation_y[index]:
                total_return += ape_amount
                good_trades += 1
            else:
                total_return += -(ape_amount / 2)
                bad_trades += 1

    logger.info(f"Total return: {total_return}, Good trades: {good_trades}, Bad trades: {bad_trades}")


if __name__ == '__main__':
    load_dotenv()
    use_cached_data = True
    asyncio.run(evaluate_model(use_cache=use_cached_data))

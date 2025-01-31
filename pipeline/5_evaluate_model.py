import asyncio
import logging
from typing import List

import pandas as pd
from dotenv import load_dotenv

from config.config_reader import load_yaml_to_dict
from constants import CONFIG_2_FILE
from data.dataset import prepare_dataset
from evaluation.simulate_trade import run_simulation
from ml_model.hist_gradient_model_builder import HistGradientBoostModelBuilder
from ml_model.model_evaluation import print_evaluation

logger = logging.getLogger(__name__)


def analyse_model(model_name: str, val: pd.DataFrame, config: dict):
    # Todo implement a way to save the Builder class info as well so we can load it properly and test multible different model types.
    # # Split the class path into module and class name
    # module_path, class_name = model_name.rsplit('.', 1)
    # # Dynamically import the module
    # module = importlib.import_module(module_path)
    print("*" * 50)
    print(f"Analysing model: {model_name.upper()}")
    model_builder = HistGradientBoostModelBuilder(dict())
    model_builder.load_model(model_name)
    val_x, val_y = model_builder.prepare_prediction_data(val.copy(), True)
    val_predictions = model_builder.predict(val_x)
    print("*" * 50)
    print_evaluation(list(val_y), val_predictions)
    print("*" * 50)
    run_simulation(val, list(val_y), val_predictions, config)
    print("*" * 50)
    print("\n" * 3)


def analyse_models(models: List[str], val: pd.DataFrame, config: dict):
    for model in models:
        analyse_model(model, val, config)


async def evaluate_models(use_cache: bool):
    config = dict()  # todo load config file
    data_config = load_yaml_to_dict(CONFIG_2_FILE)
    _, val, _ = await prepare_dataset(use_cache, data_config)

    models = config.get("models", ["hist_gradient"])
    analyse_models(models, val, data_config)


if __name__ == '__main__':
    load_dotenv()
    logging.basicConfig(level=logging.WARNING)
    use_cached_data = True
    asyncio.run(evaluate_models(use_cache=use_cached_data))

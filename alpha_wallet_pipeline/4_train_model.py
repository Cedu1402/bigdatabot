import asyncio

from dotenv import load_dotenv

from config.config_reader import load_yaml_to_dict
from constants import RANDOM_SEED, CONFIG_2_FILE
from data.dataset import prepare_dataset
from data.random_seed import set_random_seed
from ml_model.buy_all_model import BuyAllModel
from ml_model.hist_gradient_model_builder import HistGradientBoostModelBuilder
from ml_model.random_forest_model_builder import RandomForestModelBuilder


async def train_model(use_cache: bool):
    data_config = load_yaml_to_dict(CONFIG_2_FILE)
    train, val, test = await prepare_dataset(use_cache, data_config)
    config = dict()

    model = BuyAllModel(data_config)
    train = model.prepare_dataset(train, False)
    val = model.prepare_dataset(val, True)

    model.build_model()
    model.train(train, val)
    model.save()


if __name__ == '__main__':
    load_dotenv()
    set_random_seed(RANDOM_SEED)
    use_cached_data = True
    asyncio.run(train_model(use_cached_data))

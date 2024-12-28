import asyncio

from dotenv import load_dotenv

from config.config_reader import load_yaml_to_dict
from constants import RANDOM_SEED, CONFIG_2_FILE
from data.dataset import prepare_dataset
from data.random_seed import set_random_seed
from ml_model.lstm_model import LSTMModel


async def train_model(use_cache: bool):
    data_config = load_yaml_to_dict(CONFIG_2_FILE)
    train, val, test = await prepare_dataset(use_cache, data_config)
    config = dict()

    model = LSTMModel(config)
    train_x, train_y, val_x, val_y, test_x, test_y = model.prepare_train_data(train, val, test)
    config["columns"] = train_x[0].shape[1]
    config["hidden_size"] = 350
    config["epochs"] = 50

    model.build_model()
    model.train(train_x, train_y, val_x, val_y)
    model.save()


if __name__ == '__main__':
    load_dotenv()
    set_random_seed(RANDOM_SEED)
    use_cached_data = True
    asyncio.run(train_model(use_cached_data))

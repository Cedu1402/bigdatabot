import asyncio

from dotenv import load_dotenv

from config.config_reader import load_yaml_to_dict
from constants import CONFIG_2_FILE, RANDOM_SEED
from data.dataset import prepare_dataset
from data.random_seed import set_random_seed


async def prepare_data_set(use_cache: bool):
    config = load_yaml_to_dict(CONFIG_2_FILE)
    return await prepare_dataset(use_cache, config)


if __name__ == '__main__':
    load_dotenv()
    set_random_seed(RANDOM_SEED)
    use_cached_data = True
    asyncio.run(prepare_data_set(use_cached_data))

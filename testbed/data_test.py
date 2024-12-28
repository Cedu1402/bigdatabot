import asyncio

from config.config_reader import load_yaml_to_dict
from constants import CONFIG_2_FILE
from data.dataset import prepare_dataset


async def test_run():
    data_config = load_yaml_to_dict(CONFIG_2_FILE)
    train, val, test = await prepare_dataset(True, data_config)




if __name__ == '__main__':
    asyncio.run(test_run())

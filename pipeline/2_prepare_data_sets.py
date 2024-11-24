from dotenv import load_dotenv

from config.config_reader import load_yaml_to_dict
from constants import CONFIG_2_FILE
from data.dataset import prepare_dataset


def prepare_data_set(use_cache: bool):
    config = load_yaml_to_dict(CONFIG_2_FILE)
    return prepare_dataset(use_cache, config)


if __name__ == '__main__':
    load_dotenv()
    use_cached_data = True
    prepare_data_set(use_cached_data)

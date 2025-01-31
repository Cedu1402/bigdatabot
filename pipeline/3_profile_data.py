import asyncio

from dotenv import load_dotenv

from config.config_reader import load_yaml_to_dict
from constants import RANDOM_SEED, CONFIG_2_FILE, TRAIN_VAL_TEST_FILE
from data.cache_data import read_cache_data_with_config
from data.dataset import log_class_distribution
from data.random_seed import set_random_seed
from data_profile.token_stats import print_token_stats


async def profile_data(use_cache: bool):
    data_config = load_yaml_to_dict(CONFIG_2_FILE)
    data, val, test = read_cache_data_with_config(TRAIN_VAL_TEST_FILE, data_config)

    print_token_stats(data)
    print_token_stats(val, "Validation")
    print_token_stats(test, "Test")
    log_class_distribution(data, val, test)
    
    # profile = ProfileReport(data, title="Pandas Profiling Report", explorative=True)
    #
    # # Save the report to a file
    # profile.to_file("train_data_report.html")


if __name__ == '__main__':
    load_dotenv()
    set_random_seed(RANDOM_SEED)
    use_cached_data = True
    asyncio.run(profile_data(use_cached_data))

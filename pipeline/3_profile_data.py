from dotenv import load_dotenv
from ydata_profiling import ProfileReport

from constants import RANDOM_SEED
from data.dataset import prepare_dataset
from data.random_seed import set_random_seed
from data.sliding_window import unroll_data


def profile_data(use_cache: bool):
    train, val, test = prepare_dataset(use_cache)
    validation = prepare_dataset(use_cache)

    train_full = unroll_data(train)

    print(train_full.describe())

    profile = ProfileReport(train_full, title="Pandas Profiling Report", explorative=True)

    # Save the report to a file
    profile.to_file("train_data_report.html")


if __name__ == '__main__':
    load_dotenv()
    set_random_seed(RANDOM_SEED)
    use_cached_data = True
    profile_data(use_cached_data)

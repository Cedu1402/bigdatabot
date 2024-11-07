from dotenv import load_dotenv

from data.dataset import prepare_dataset


def prepare_data_set(use_cache: bool):
    return prepare_dataset(use_cache)


if __name__ == '__main__':
    load_dotenv()
    use_cached_data = True
    prepare_data_set(use_cached_data)

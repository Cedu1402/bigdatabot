from dotenv import load_dotenv

from dune.data_collection import collect_all_data


def main(use_cache: bool):
    load_dotenv()
    data = collect_all_data(use_cache)


if __name__ == '__main__':
    use_cached_data = True
    collect_all_data(use_cached_data)
    main(use_cached_data)

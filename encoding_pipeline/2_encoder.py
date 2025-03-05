import pandas as pd
from flask.cli import load_dotenv

from constants import TOKEN_COLUMN, TRADING_MINUTE_COLUMN
from data.cache_data import save_cache_data, read_cache_data
from database.token_sample_table import get_all_samples


def main():
    # token_samples = get_all_samples()
    full_data = pd.DataFrame()
    token_samples = read_cache_data('token_samples')
    for sample in token_samples:
        full_data = pd.concat([full_data, sample.raw_data], ignore_index=True)

    full_data.reset_index(drop=True, inplace=True)
    full_data.sort_values(by=[TOKEN_COLUMN, TRADING_MINUTE_COLUMN], inplace=True)
    save_cache_data('token_samples_full', full_data)


if __name__ == '__main__':
    load_dotenv()
    main()

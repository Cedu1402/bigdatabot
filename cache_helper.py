import os
import pickle
from typing import Union, Optional

import pandas as pd

from constants import CACHE_FOLDER


def get_cache_file_data(query_id: Union[int, str]) -> Optional[pd.DataFrame]:
    if cache_exists(str(query_id)):
        return get_cache_data(str(query_id))
    return None


def write_data_to_cache(name, data):
    """Write data to a pickle file in the cache directory."""
    os.makedirs(CACHE_FOLDER, exist_ok=True)
    with open(get_cache_file_path(name), 'wb') as f:  # Use 'wb' for binary write
        pickle.dump(data, f)


def get_cache_file_path(name):
    return os.path.join(CACHE_FOLDER, f'{name}.pkl')


def cache_exists(name):
    """Check if a cache file exists."""
    return os.path.exists(get_cache_file_path(name))  # Change to .pkl extension


def get_cache_data(name):
    """Read data from a cache file."""
    try:
        with open(get_cache_file_path(name), 'rb') as f:  # Use 'rb' for binary read
            return pickle.load(f)
    except FileNotFoundError:
        return None

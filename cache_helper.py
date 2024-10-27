import os
import pickle

def write_data_to_cache(name, data):
    """Write data to a pickle file in the cache directory."""
    os.makedirs('cache', exist_ok=True)
    with open(f'cache/{name}.pkl', 'wb') as f:  # Use 'wb' for binary write
        pickle.dump(data, f)

def cache_exists(name):
    """Check if a cache file exists."""
    return os.path.exists(f'cache/{name}.pkl')  # Change to .pkl extension

def get_cache_data(name):
    """Read data from a cache file."""
    try:
        with open(f'cache/{name}.pkl', 'rb') as f:  # Use 'rb' for binary read
            return pickle.load(f)
    except FileNotFoundError:
        return None

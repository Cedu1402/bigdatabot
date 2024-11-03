import os
import pickle


def save_to_pickle(data, filename):
    """Save data to a pickle file."""
    dir_path = os.path.dirname(filename)

    if dir_path:
        os.makedirs(dir_path, exist_ok=True)

    with open(filename, 'wb') as file:
        pickle.dump(data, file)


def load_from_pickle(filename):
    """Load data from a pickle file."""
    if not os.path.exists(filename):
        return None

    with open(filename, 'rb') as file:
        return pickle.load(file)


def pickle_deep_copy(item):
    return pickle.loads(pickle.dumps(item))

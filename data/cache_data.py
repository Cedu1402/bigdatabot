import os

from config.config_reader import hash_config
from constants import CACHE_FOLDER
from data.pickle_files import load_from_pickle, save_to_pickle


def read_cache_data_with_config(file_name_base: str, config: dict):
    file_name = file_name_base + hash_config(config)
    return read_cache_data(file_name)


def read_cache_data(file_name_base: str):
    if os.path.exists(os.path.join(CACHE_FOLDER, file_name_base + ".pkl")):
        return load_from_pickle(os.path.join(CACHE_FOLDER, file_name_base + ".pkl"))
    return None


def save_cache_data_with_config(file_name_base: str, config: dict, data):
    # Generate the filename based on the config hash
    file_name = file_name_base + hash_config(config)
    save_cache_data(file_name, data)


def save_cache_data(file_name_base: str, data):
    # Define the full file path
    file_path = os.path.join(CACHE_FOLDER, file_name_base + ".pkl")

    # Save the data to the pickle file
    save_to_pickle(data, file_path)

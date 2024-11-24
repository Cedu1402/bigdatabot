import hashlib
import json

import yaml


def load_yaml_to_dict(file_path: str) -> dict:
    """
    Load a YAML file into a Python dictionary.

    Args:
        file_path (str): Path to the YAML file.

    Returns:
        dict: Dictionary containing the parsed YAML data.
    """
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)


def hash_config(config: dict) -> str:
    """
    Generate a hash for the given configuration dictionary.

    Args:
        config (dict): Configuration dictionary.

    Returns:
        str: A unique hash string.
    """
    config_str = json.dumps(config, sort_keys=True)  # Ensure consistent order for hashing
    return hashlib.sha256(config_str.encode()).hexdigest()

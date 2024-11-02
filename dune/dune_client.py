from dune_client.client import DuneClient

from constants import DUNE_API_KEY
from env_data.get_env_value import get_env_value
from log import logger


def get_dune_client():
    key = get_env_value(DUNE_API_KEY)
    if key is None:
        logger.error("Failed to get Dune client.")
        return None
    return DuneClient(get_env_value(DUNE_API_KEY))

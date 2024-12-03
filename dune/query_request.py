from typing import Optional

import pandas as pd
from dune_client.models import ResultsResponse

from cache_helper import cache_exists, get_cache_data, write_data_to_cache
from dune.data_transform import transform_dune_result_to_pandas
from dune.dune_client import get_dune_client
from structure_log.logger_setup import logger


def get_cache_file_data(query_id: int) -> Optional[ResultsResponse]:
    if cache_exists(str(query_id)):
        return get_cache_data(str(query_id))
    return None


def fetch_query_data(query_id: int, read_from_cache: bool) -> Optional[ResultsResponse]:
    """Fetch query results from cache or API based on the read_from_cache flag."""
    if read_from_cache:
        result_data = get_cache_file_data(query_id)
        if result_data is not None:
            return result_data  # Return cached data if available

    # Fallback to API if no cached data or not reading from cache
    return get_from_api(query_id)


def get_query_result(query_id: int, read_from_cache=True) -> Optional[pd.DataFrame]:
    logger.info(f"Fetching query result for query ID: {query_id}")
    query_result = fetch_query_data(query_id, read_from_cache)
    if query_result is None:
        logger.warning("Failed to get query result for query ID: %s", query_id)
        return None

    df = transform_dune_result_to_pandas(query_result)
    return df


def get_from_api(query_id: int) -> Optional[ResultsResponse]:
    # Initialize Dune client
    dune_client = get_dune_client()
    if dune_client is None:
        return None

    try:
        # Fetch the latest result from Dune
        query_result = dune_client.get_latest_result(query_id)
        write_data_to_cache(query_id, query_result)
        return query_result
    except Exception as e:
        logger.exception(e, "An unexpected error occurred while fetching query result.")
        return None


def get_from_cache(query_id: int) -> Optional[ResultsResponse]:
    cached_file = get_cache_file_data(query_id)
    if cached_file is not None:
        return cached_file

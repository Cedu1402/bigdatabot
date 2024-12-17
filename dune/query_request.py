import logging
from typing import Optional, Dict, Any, Union

import pandas as pd
from dune_client.models import ResultsResponse
from dune_client.query import QueryBase
from dune_client.types import QueryParameter

from cache_helper import cache_exists, get_cache_data, write_data_to_cache
from config.config_reader import hash_config
from dune.data_transform import transform_dune_result_to_pandas
from dune.dune_client import get_dune_client

logger = logging.getLogger(__name__)


def get_cache_file_data(query_id: Union[int, str]) -> Optional[ResultsResponse]:
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
        logger.exception("An unexpected error occurred while fetching query result.")
        return None


def get_from_cache(query_id: int) -> Optional[ResultsResponse]:
    cached_file = get_cache_file_data(query_id)
    if cached_file is not None:
        return cached_file


def fetch_query_data_with_params(
        query_id: int, params: Optional[Dict[str, Any]], read_from_cache: bool = True
) -> Optional[ResultsResponse]:
    """
    Fetches query data with parameters, either from cache or Dune API.
    """
    if read_from_cache:
        cache_id = get_cache_id(query_id, params)
        result_data = get_cache_file_data(cache_id)
        if result_data is not None:
            return result_data  # Return cached data if available

    # Fallback to API if no cached data or cache read is disabled
    return get_from_api_with_params(query_id, params)


def get_query_result_with_params(
        query_id: int, params: Optional[Dict[str, Any]] = None, read_from_cache: bool = True
) -> Optional[pd.DataFrame]:
    """
    Fetches and transforms query results into a pandas DataFrame.
    """
    logger.info(f"Fetching query result for query ID: {query_id} with params: {params}")
    query_result = fetch_query_data_with_params(query_id, params, read_from_cache)
    if query_result is None:
        logger.warning("Failed to get query result for query ID: %s with params: %s", query_id, params)
        return None

    df = transform_dune_result_to_pandas(query_result)
    return df


def get_cache_id(query_id: int, params: Optional[Dict[str, Any]]) -> str:
    return str(query_id) + "_" + hash_config(params)


def get_from_api_with_params(query_id: int, params: Optional[Dict[str, Any]]) -> Optional[ResultsResponse]:
    """
    Fetches query results from the Dune API with parameters and caches the result.
    """
    # Initialize Dune client
    dune_client = get_dune_client()
    if dune_client is None:
        return None

    try:
        # Fetch the result from Dune API with parameters
        dune_params = serialize_params(params)
        query = QueryBase(
            name="My query",
            query_id=query_id,
            params=dune_params,
        )

        # Fetch results from the Dune API
        query_result = dune_client.get_latest_result(query)

        cache_id = get_cache_id(query_id, params)
        write_data_to_cache(cache_id, query_result)
        return query_result
    except Exception as e:
        logger.exception("An unexpected error occurred while fetching query result with params.")
        return None


def serialize_params(params: Dict[str, Any]) -> list[QueryParameter]:
    """
    Converts a dictionary of params into a list of QueryParameter objects.
    """
    dune_params = []
    for key, value in params.items():
        if isinstance(value, (int, float)):
            dune_params.append(QueryParameter.number_type(name=key, value=value))
        elif isinstance(value, str):
            dune_params.append(QueryParameter.text_type(name=key, value=value))
        elif isinstance(value, bool):
            dune_params.append(QueryParameter.enum_type(name=key, value=str(value)))
        else:
            logger.warning(f"Unsupported param type for {key}: {type(value)}")
    return dune_params

from datetime import datetime
from typing import Optional

import pandas as pd

from dune.data_transform import transform_dune_result_to_pandas
from dune.dune_client import get_dune_client
from log import logger

class CacheFileData:

    def __init__(self, file_date: datetime, name: str):
        self.file_date = file_date
        self.name = name

    def get_filename(self) -> str:
        # Format the file_date to "YYYY-MM-DD_HH-MM-SS" for use in filenames
        date_format = self.file_date.strftime('%Y-%m-%d_%H-%M-%S')
        # Combine the formatted date with the name
        return f"{self.name}_{date_format}.pkl"

    def check_file(self, name: str) -> :

def get_cache_file_data(query_id: int) -> str:

    return query_id + ".pkl"

def get_query_result(query_id: int) -> Optional[pd.DataFrame]:
    logger.info(f"Fetching query result for query ID: {query_id}")

    # Initialize Dune client
    dune_client = get_dune_client()
    if dune_client is None:
        return None

    try:
        # Fetch the latest result from Dune
        query_result = dune_client.get_latest_result(query_id)

        # Check for errors in the response
        if 'error' in query_result:
            error_message = query_result['error']['message']
            logger.error(f"Dune API Error: {error_message}")
            return None

        # Convert the result to a DataFrame and return
        df = transform_dune_result_to_pandas(query_result)
        return df
    except Exception as e:
        logger.exception(e, "An unexpected error occurred while fetching query result.")
        return None

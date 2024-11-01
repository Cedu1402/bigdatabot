from typing import Optional

import pandas as pd
from dune_client.models import ResultsResponse


def transform_dune_result_to_pandas(query_result: ResultsResponse) -> Optional[pd.DataFrame]:
    try:
        # Extract rows from the ResultsResponse object
        rows = query_result.result.rows

        # If no rows, return empty DataFrame
        if not rows:
            return pd.DataFrame()

        # Convert list of dictionaries to DataFrame
        df = pd.DataFrame(rows)

        # Convert data types if metadata is available
        if hasattr(query_result.result, 'metadata'):
            metadata = query_result.result.metadata
            if hasattr(metadata, 'column_types') and hasattr(metadata, 'column_names'):
                type_mapping = dict(zip(
                    metadata.column_names,
                    metadata.column_types
                ))

                # Convert types based on Dune's type information
                for column, dtype in type_mapping.items():
                    if column in df.columns:
                        if dtype in ['number', 'integer']:
                            df[column] = pd.to_numeric(df[column])
                        elif dtype == 'timestamp':
                            df[column] = pd.to_datetime(df[column])
                        # Keep strings as is

        return df

    except Exception as e:
        raise ValueError(f"Failed to convert Dune response to DataFrame: {str(e)}")

import pandas as pd


def transform_dune_result_to_pandas(query_result):
    if query_result is None or 'data' not in query_result:
        print("No results found or error in query.")
        return None

    # Access the columns and rows from the query result
    columns = query_result['data']['columns']
    rows = query_result['data']['rows']

    # Create a DataFrame using the column names and rows
    df = pd.DataFrame(rows, columns=[col['name'] for col in columns])

    return df

import logging
import pickle

from database.db_connection import get_db_connection
from dto.token_dataset_model import TokenDataset

logger = logging.getLogger(__name__)


def insert_token_dataset(token_dataset: TokenDataset):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                # Prepare the SQL INSERT statement
                insert_query = """
                INSERT INTO token_dataset (token, trading_minute, raw_data)
                VALUES (%s, %s, %s)
                """

                # Execute the INSERT query with the token dataset data
                cursor.execute(insert_query, (
                    token_dataset.token,
                    token_dataset.trading_minute,
                    pickle.dumps(token_dataset.raw_data)
                ))

                # Commit the transaction
                conn.commit()
    except Exception as e:
        logger.exception("Failed to insert token dataset", extra={"token": token_dataset.token})


def get_token_datasets_by_token(token: str) -> list[TokenDataset]:
    """
    Fetches all token datasets for a given token.

    Args:
        token (str): The token to filter datasets.

    Returns:
        list[TokenDataset]: A list of TokenDataset objects.
    """
    datasets = []
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                # Prepare the SQL SELECT statement
                select_query = """
                SELECT token, trading_minute, raw_data
                FROM token_dataset
                WHERE token = %s
                ORDER BY trading_minute
                """

                # Execute the SELECT query
                cursor.execute(select_query, (token,))
                rows = cursor.fetchall()

                # Deserialize and convert to TokenDataset objects
                for row in rows:
                    datasets.append(TokenDataset(
                        token=row[0],
                        trading_minute=row[1],
                        raw_data=pickle.loads(row[2])
                    ))
    except Exception as e:
        logger.exception("Failed to fetch token datasets", extra={"token": token})

    return datasets


def get_token_datasets_by_daterange(from_date, to_date) -> dict[str, list[TokenDataset]]:
    """
    Fetches token datasets within a date range.

    Args:
        from_date (datetime): The start of the date range.
        to_date (datetime): The end of the date range.

    Returns:
        dict[str, list[TokenDataset]]: A dictionary where the key is the token
                                        and the value is a list of TokenDataset objects.
    """
    token_datasets = {}
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                # Prepare the SQL SELECT statement
                select_query = """
                SELECT token, trading_minute, raw_data
                FROM token_dataset
                WHERE trading_minute BETWEEN %s AND %s
                ORDER BY token, trading_minute
                """

                # Execute the SELECT query
                cursor.execute(select_query, (from_date, to_date))
                rows = cursor.fetchall()

                # Deserialize and organize into dictionary
                for row in rows:
                    token = row[0]
                    dataset = TokenDataset(
                        token=row[0],
                        trading_minute=row[1],
                        raw_data=pickle.loads(row[2])
                    )
                    if token not in token_datasets:
                        token_datasets[token] = []
                    token_datasets[token].append(dataset)
    except Exception as e:
        logger.exception("Failed to fetch token datasets by date range",
                         extra={"from_date": from_date, "to_date": to_date})

    return token_datasets

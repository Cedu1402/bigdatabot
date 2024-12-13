import logging
from datetime import datetime
from typing import Optional

from database.db_connection import get_db_connection

logger = logging.getLogger(__name__)


def insert_token_watch(token: str, start_time: datetime, end_time: Optional[datetime]) -> int:
    """
    Inserts a token watch entry into the token_watch table and returns the inserted row's ID.

    Args:
        token (str): The token being watched.
        start_time (datetime): The start time of the watch period.
        end_time (datetime): The end time of the watch period.

    Returns:
        int: The ID of the inserted row.
    """
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                # Prepare the SQL INSERT statement
                insert_query = """
                INSERT INTO token_watch (token, start_time, end_time)
                VALUES (%s, %s, %s) RETURNING id
                """

                # Execute the INSERT query with the token watch data
                cursor.execute(insert_query, (token, start_time, end_time))

                # Fetch the ID of the inserted row
                inserted_id = cursor.fetchone()[0]

                # Commit the transaction
                conn.commit()

                return inserted_id
    except Exception as e:
        logger.exception("Failed to insert token watch", extra={
            "token": token,
            "start_time": start_time,
            "end_time": end_time
        })


def token_watch_exists(token: str) -> bool:
    """
    Checks if a token watch record exists in the token_watch table.

    Args:
        token (str): The token to check.

    Returns:
        bool: True if the token watch exists, False otherwise.
    """
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                # Prepare the SQL SELECT statement to check for the token
                select_query = """
                SELECT 1
                FROM token_watch
                WHERE token = %s
                LIMIT 1
                """

                # Execute the SELECT query with the provided token
                cursor.execute(select_query, (token,))
                result = cursor.fetchone()

                # Return True if the token watch exists, False otherwise
                return result is not None
    except Exception as e:
        logger.exception("Failed to check if token watch exists", extra={"token": token})
        return False

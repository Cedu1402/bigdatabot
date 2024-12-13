import logging
from datetime import datetime
from typing import Optional, Tuple

from database.db_connection import get_db_connection

logger = logging.getLogger(__name__)


def set_end_time(token: str, end_time: datetime) -> bool:
    """
    Updates the end time for an existing token watch entry.

    Args:
        token (str): The token whose end time needs to be updated.
        end_time (datetime): The new end time to set.

    Returns:
        bool: True if the update was successful, False otherwise.
    """
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                # Prepare the SQL UPDATE statement
                update_query = """
                UPDATE token_watch
                SET end_time = %s
                WHERE token = %s
                AND end_time IS NULL
                RETURNING id
                """

                # Execute the UPDATE query
                cursor.execute(update_query, (end_time, token))

                # Check if a row was updated (id should be returned)
                updated_row = cursor.fetchone()

                if updated_row:
                    # Commit the transaction if the row was updated
                    conn.commit()
                    logger.info(f"End time updated for token: {token}", extra={"token": token, "end_time": end_time})
                    return True
                else:
                    logger.warning(f"No record found or already has an end time for token: {token}",
                                   extra={"token": token})
                    return False
    except Exception as e:
        logger.exception("Failed to update end time", extra={"token": token, "end_time": end_time})
        return False


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


def get_token_watch(token: str) -> Optional[Tuple[int, str, datetime, Optional[datetime]]]:
    """
    Retrieves all information for a token watch entry from the token_watch table.

    Args:
        token (str): The token whose watch entry to retrieve.

    Returns:
        Optional[Tuple[int, str, datetime, Optional[datetime]]]:
            A tuple containing the id, token, start_time, and end_time if found,
            or None if no entry is found for the given token.
    """
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                # Prepare the SQL SELECT statement to fetch all data for the token
                select_query = """
                SELECT id, token, start_time, end_time
                FROM token_watch
                WHERE token = %s
                LIMIT 1
                """

                # Execute the SELECT query with the provided token
                cursor.execute(select_query, (token,))
                result = cursor.fetchone()

                # Return the result tuple or None if no record is found
                return result
    except Exception as e:
        logger.exception("Failed to fetch token watch", extra={"token": token})
        return None

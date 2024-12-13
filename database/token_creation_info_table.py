import logging
from datetime import datetime
from typing import Optional, Tuple

from database.db_connection import get_db_connection

logger = logging.getLogger(__name__)


def insert_token_creation_info(token: str, creator: str, timestamp: datetime):
    """
    Inserts token creation information into the token_creation_info table.

    Args:
        token (str): The token name or identifier.
        creator (str): The creator's address or identifier.
        timestamp (datetime): The timestamp of the token creation.
    """
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                # Prepare the SQL INSERT statement
                insert_query = """
                INSERT INTO token_creation_info (token, creator, timestamp)
                VALUES (%s, %s, %s)
                """

                # Execute the INSERT query with the token creation data
                cursor.execute(insert_query, (token, creator, timestamp))

                # Commit the transaction
                conn.commit()
    except Exception as e:
        logger.exception("Failed to insert token creation info", extra={
            "token": token,
            "creator": creator,
            "timestamp": timestamp
        })


def select_token_creation_info(token: str) -> Optional[Tuple[datetime, str]]:
    """
    Selects token creation information from the token_creation_info table.

    Args:
        token (str): The token name or identifier to query.

    Returns:
        tuple: A tuple containing (timestamp, creator) if found, else None.
    """
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                # Prepare the SQL SELECT statement
                select_query = """
                SELECT timestamp, creator
                FROM token_creation_info
                WHERE token = %s
                """

                # Execute the SELECT query with the provided token
                cursor.execute(select_query, (token,))
                result = cursor.fetchone()

                if result:
                    # Return timestamp as datetime object and creator as string
                    return result[0], result[1]
                else:
                    return None
    except Exception as e:
        logger.exception("Failed to retrieve token creation info", extra={"token": token})
        return None

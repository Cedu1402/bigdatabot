import logging
from datetime import datetime

from database.db_connection import get_db_connection

logger = logging.getLogger(__name__)


def insert_event(wallet: str, time: datetime, signature: str):
    """
    Inserts an event into the event table.

    Args:
        wallet (str): The Solana wallet address.
        time (str): The timestamp of the event.
        signature (str): The transaction signature.
    """
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                # Prepare the SQL INSERT statement
                insert_query = """
                INSERT INTO event (wallet, time, signature)
                VALUES (%s, %s, %s)
                """

                # Execute the INSERT query with the event data
                cursor.execute(insert_query, (wallet, time.isoformat(), signature))

                # Commit the transaction
                conn.commit()
    except Exception as e:
        logger.exception("Failed to insert event", extra={
            "wallet": wallet,
            "time": time,
            "signature": signature
        })

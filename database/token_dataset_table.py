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

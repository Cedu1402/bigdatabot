import logging
import pickle
from typing import Optional

from database.db_connection import get_db_connection
from dto.token_sample_model import TokenSample

logger = logging.getLogger(__name__)


def insert_token_sample(token_sample: TokenSample):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                insert_query = """
                INSERT INTO token_sample (token, raw)
                VALUES (%s, %s)
                """
                cursor.execute(insert_query, (
                    token_sample.token,
                    pickle.dumps(token_sample.raw_data)
                ))
                conn.commit()
    except Exception as e:
        logger.exception("Failed to insert token sample", extra={"token": token_sample.token})


def get_token_samples_by_token(token: str) -> Optional[TokenSample]:
    """
    Fetches all token samples for a given token.

    Args:
        token (str): The token to filter samples.

    Returns:
        Optional[TokenSample]: TokenSample object.
    """
    
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                select_query = """
                SELECT id, token, raw
                FROM token_sample
                WHERE token = %s
                ORDER BY id
                """
                cursor.execute(select_query, (token,))
                rows = cursor.fetchall()
                for row in rows:
                    return TokenSample(
                        token=row[1],
                        raw_data=pickle.loads(row[2])
                    )
    except Exception as e:
        logger.exception("Failed to fetch token samples", extra={"token": token})
    return None

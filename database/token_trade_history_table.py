import logging

from database.db_connection import get_db_connection
from dto.token_trade_history_model import TokenTradeHistory

logger = logging.getLogger(__name__)


def insert_token_trade_history(token_trade_history: TokenTradeHistory):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                # Prepare the SQL INSERT statement
                insert_query = """
                INSERT INTO token_trade_history (token, buy_time, sell_time, buy_price, sell_price)
                VALUES (%s, %s, %s, %s, %s)
                """

                # Execute the INSERT query with the token trade history data
                cursor.execute(insert_query, (
                    token_trade_history.token,
                    token_trade_history.buy_time,
                    token_trade_history.sell_time,
                    token_trade_history.buy_price,
                    token_trade_history.sell_price
                ))

                # Commit the transaction
                conn.commit()
    except Exception as e:
        logger.exception("Failed to insert token trade history",
                         extra={"token_trade_history": token_trade_history.token})

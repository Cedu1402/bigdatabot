import logging

from database.db_connection import get_db_connection
from dto.trade_model import Trade

logger = logging.getLogger(__name__)


def insert_trade(trade: Trade):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:

                # Prepare the SQL INSERT statement
                insert_query = """
               INSERT INTO trades (trader, token, token_amount, sol_amount, buy, token_holding_after, trade_time, tx_signature)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
               """

                # Execute the INSERT query with the trade data
                cursor.execute(insert_query, (
                    trade.trader,
                    trade.token,
                    trade.token_amount,
                    trade.sol_amount,
                    trade.buy,
                    trade.token_holding_after,
                    trade.get_time(),
                    trade.tx_signature
                ))

                # Commit the transaction
                conn.commit()
    except Exception as e:
        logger.exception("Failed to insert trade", extra={"trade": trade.to_dict()})

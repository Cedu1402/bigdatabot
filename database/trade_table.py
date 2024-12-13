import logging
from typing import List

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


def get_trades_by_token(token: str) -> List[Trade]:
    """
    Retrieves all trades for a given token.

    Args:
        token (str): The token for which trades need to be fetched.

    Returns:
        List[Trade]: A list of Trade objects representing the trades for the given token.
    """
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                # Prepare the SQL SELECT statement to retrieve all trades for the given token
                select_query = """
                SELECT trader, token, token_amount, sol_amount, buy, token_holding_after, trade_time, tx_signature
                FROM trades
                WHERE token = %s
                """

                # Execute the SELECT query with the provided token
                cursor.execute(select_query, (token,))

                # Fetch all results
                rows = cursor.fetchall()

                # Map the rows to Trade objects
                trades = [
                    Trade(
                        trader=row[0],
                        token=row[1],
                        token_amount=row[2],
                        sol_amount=row[3],
                        buy=row[4],
                        token_holding_after=row[5],
                        trade_time=row[6].isoformat(),
                        tx_signature=row[7]
                    )
                    for row in rows
                ]

                return trades

    except Exception as e:
        logger.exception(f"Failed to fetch trades for token {token}")
        return []

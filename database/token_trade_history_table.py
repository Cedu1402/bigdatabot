import logging
from datetime import datetime
from typing import Dict

from constants import INVESTMENT_AMOUNT
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


def get_trade_stats() -> Dict[str, float]:
    """
    Retrieves the total number of trades and the total percentage return
    from the token_trade_history table.

    Returns:
        Dict[str, float]: A dictionary with the total trades and total percentage return.
    """
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                # Query to get the total number of trades and the total percentage return
                query = """
                SELECT 
                    COUNT(*) AS total_trades,
                    SUM((sell_price - buy_price) / buy_price * %s) AS total_return
                FROM token_trade_history WHERE buy_time > '2025-01-05 11:40:00' AND sell_price IS NOT NULL
                """
                cursor.execute(query, (INVESTMENT_AMOUNT,))
                result = cursor.fetchone()

                if result:
                    total_trades, total_return = result
                    return {
                        "total_trades": total_trades or 0,
                        "total_return": total_return or 0.0
                    }
                else:
                    return {
                        "total_trades": 0,
                        "total_return": 0.0
                    }
    except Exception as e:
        logger.exception("Failed to retrieve trade stats")
        return {
            "total_trades": 0,
            "total_return": 0.0
        }


def get_open_trades() -> int:
    """
    Retrieves the total number of open trades.

    Returns:
       int: Amount of open trades.
    """
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                # Query to get the total number of trades and the total percentage return
                query = """
                SELECT 
                    COUNT(*) AS open_trades
                FROM token_trade_history WHERE buy_time > '2025-01-02 06:40:00' AND sell_price IS NULL
                """
                cursor.execute(query)
                result = cursor.fetchone()

                if result:
                    return result[0]
                else:
                    return 0
    except Exception as e:
        logger.exception("Failed to retrieve trade stats")
        return 0


def update_sell_price(token: str, sell_price: float):
    """
    Updates the sell price for a specific token in the token_trade_history table.

    Args:
        token (str): The token identifier for which the sell price needs to be updated.
        sell_price (float): The new sell price to be updated.
        sell_time (datetime): The new sell time to be updated.
    Returns:
        bool: True if the update was successful, False otherwise.
    """
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                # Prepare the SQL UPDATE statement
                update_query = """
                UPDATE token_trade_history
                SET sell_price = %s, sell_time = %s
                WHERE token = %s
                """

                # Execute the UPDATE query
                cursor.execute(update_query, (sell_price, datetime.utcnow(), token))

                # Commit the transaction
                conn.commit()
    except Exception as e:
        logger.exception("Failed to update sell price", extra={"token": token, "sell_price": sell_price})
        return False

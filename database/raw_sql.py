import logging

from database.db_connection import get_db_connection

logger = logging.getLogger(__name__)


def run_sql_file(sql_file_path: str):
    try:
        # Connect to the PostgreSQL database
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                # Read the SQL file
                with open(sql_file_path, 'r') as file:
                    sql_script = file.read()

                # Execute the SQL script
                cursor.execute(sql_script)
                conn.commit()

    except Exception as e:
        logger.exception("Failed to execute SQL script", extra={"file": sql_file_path})

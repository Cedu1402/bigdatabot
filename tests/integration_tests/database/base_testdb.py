import os
import unittest
from unittest.mock import patch

import psycopg2
from dotenv import load_dotenv
from psycopg2 import sql

from constants import POSTGRES_USER, POSTGRES_PASSWORD, ROOT_DIR
from database.raw_sql import run_sql_file
from env_data.get_env_value import get_env_value


class BaseTestDatabase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db_name_patcher = patch('database.db_connection.DATABASE_NAME', 'testdb')
        cls.mocked_db_name = cls.db_name_patcher.start()

        load_dotenv()

        # Connect to the default database (postgres) to check for testdb
        cls.conn = psycopg2.connect(
            dbname="bigdatabot",  # Connect to an administrative database
            user=get_env_value(POSTGRES_USER),
            password=get_env_value(POSTGRES_PASSWORD),
            host="localhost"
        )

        cls.conn.autocommit = True
        cls.cursor = cls.conn.cursor()

        # Check if the database already exists
        cls.cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", ("testdb",))
        exists = cls.cursor.fetchone()

        if not exists:
            # Create the database if it doesn't exist
            cls.cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier("testdb")))
            print("Database 'testdb' created successfully!")
        else:
            print("Database 'testdb' already exists!")

        # Reconnect to the test database
        cls.conn.close()
        cls.conn = psycopg2.connect(
            dbname="testdb",
            user=get_env_value(POSTGRES_USER),
            password=get_env_value(POSTGRES_PASSWORD),
            host="localhost"
        )
        cls.cursor = cls.conn.cursor()

        # Create tables (shared setup for all tests)
        run_sql_file(os.path.join(ROOT_DIR, "database/tables.sql"))
        cls.conn.commit()

    @classmethod
    def tearDownClass(cls):
        # Delete all tables from the database
        cls.cursor.execute("""
               DO $$ 
               DECLARE
                   table_name RECORD;
               BEGIN
                   FOR table_name IN 
                       (SELECT tablename 
                        FROM pg_tables 
                        WHERE schemaname = 'public') 
                   LOOP
                       EXECUTE 'DROP TABLE IF EXISTS ' || table_name.tablename || ' CASCADE';
                   END LOOP;
               END $$;
           """)
        # Drop tables and close the connection
        cls.conn.commit()
        cls.cursor.close()
        cls.conn.close()

import os
import re

from constants import ROOT_DIR
from tests.integration_tests.database.base_testdb import BaseTestDatabase


class TestRunner(BaseTestDatabase):

    def test_run_sql_file_should_create_tables(self):
        tables_file = os.path.join(ROOT_DIR, "database/tables.sql")
        # Step 1: Read the SQL file
        with open(tables_file, 'r') as file:
            sql_content = file.read()

        # Step 2: Extract table names using a regex
        table_names = re.findall(r'CREATE TABLE IF NOT EXISTS (\w+)', sql_content)

        # Step 3: Query the database to check if tables exist
        for table in table_names:
            self.cursor.execute(
                "SELECT EXISTS (SELECT 1 FROM pg_tables WHERE tablename = %s);",
                (table,)
            )
            exists = self.cursor.fetchone()[0]
            self.assertTrue(exists, f"Table {table} does not exist in the database.")

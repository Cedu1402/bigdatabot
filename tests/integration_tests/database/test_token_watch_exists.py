from datetime import datetime, timedelta

from database.token_watch_table import insert_token_watch, token_watch_exists
from tests.integration_tests.database.base_testdb import BaseTestDatabase


class TestRunner(BaseTestDatabase):

    def test_token_watch_exists(self):
        # Arrange
        token = "test_token"
        start_time = datetime.now()
        end_time = start_time + timedelta(hours=1)

        # Insert the token watch record for the first time
        insert_token_watch(token, start_time, end_time)

        # Act & Assert for "token watch exists"
        exists = token_watch_exists(token)
        self.assertTrue(exists, "The token watch should exist in the database after being inserted")

    def test_token_watch_does_not_exist(self):
        # Arrange
        token = "non_existing_token"

        # Act & Assert for "token watch does not exist"
        exists = token_watch_exists(token)
        self.assertFalse(exists, "The token watch should not exist in the database if it hasn't been inserted")

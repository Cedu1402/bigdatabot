from datetime import datetime, timedelta

from database.token_watch_table import insert_token_watch, get_token_watch
from tests.integration_tests.database.base_testdb import BaseTestDatabase


class TestRunner(BaseTestDatabase):

    def test_get_token_watch(self):
        # Arrange
        token = "test_token"
        start_time = datetime.now()
        end_time = start_time + timedelta(hours=1)

        # Insert the token watch record
        inserted_id = insert_token_watch(token, start_time, end_time)

        # Act
        result = get_token_watch(token)

        # Assert
        self.assertIsNotNone(result, "The token watch record should be fetched from the database")
        self.assertEqual(result[0], inserted_id, "The fetched ID should match the inserted ID")
        self.assertEqual(result[1], token, "The token should match the inserted value")
        self.assertEqual(result[2].isoformat(), start_time.isoformat(),
                         "The start time should match the inserted value")
        self.assertEqual(result[3].isoformat(), end_time.isoformat(), "The end time should match the inserted value")

    def test_get_token_watch_not_found(self):
        # Arrange
        token = "non_existing_token"

        # Act
        result = get_token_watch(token)

        # Assert
        self.assertIsNone(result, "The token watch record should not be found if it hasn't been inserted")

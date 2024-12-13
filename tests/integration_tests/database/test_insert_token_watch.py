from datetime import datetime, timedelta

from database.token_watch_table import insert_token_watch
from tests.integration_tests.database.base_testdb import BaseTestDatabase


class TestRunner(BaseTestDatabase):

    def test_insert_token_watch(self):
        # Arrange
        token = "test_token"
        start_time = datetime.now()
        end_time = start_time + timedelta(hours=1)

        # Act
        inserted_id = insert_token_watch(token, start_time, end_time)

        # Assert
        self.cursor.execute("""
            SELECT id, token, start_time, end_time
            FROM token_watch
            WHERE id = %s
        """, (inserted_id,))
        result = self.cursor.fetchone()

        self.assertIsNotNone(result, "The token watch should be inserted into the database")
        self.assertEqual(result[0], inserted_id, "The inserted ID should match the result")
        self.assertEqual(result[1], token, "The token should match the inserted value")
        self.assertEqual(result[2].isoformat(), start_time.isoformat(),
                         "The start time should match the inserted value")
        self.assertEqual(result[3].isoformat(), end_time.isoformat(), "The end time should match the inserted value")

    def test_insert_token_watch_with_none_end_time(self):
        # Arrange
        token = "test_token_none_end"
        start_time = datetime.now()
        end_time = None  # Setting end_time to None

        # Act
        inserted_id = insert_token_watch(token, start_time, end_time)

        # Assert
        self.cursor.execute("""
               SELECT id, token, start_time, end_time
               FROM token_watch
               WHERE id = %s
           """, (inserted_id,))
        result = self.cursor.fetchone()

        self.assertIsNotNone(result, "The token watch should be inserted into the database")
        self.assertEqual(result[0], inserted_id, "The inserted ID should match the result")
        self.assertEqual(result[1], token, "The token should match the inserted value")
        self.assertEqual(result[2].isoformat(), start_time.isoformat(),
                         "The start time should match the inserted value")
        self.assertIsNone(result[3], "The end time should be None (NULL) when not provided")

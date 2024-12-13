from datetime import datetime, timedelta

from database.token_watch_table import insert_token_watch, set_end_time, get_token_watch
from tests.integration_tests.database.base_testdb import BaseTestDatabase


class TestRunner(BaseTestDatabase):

    def test_set_end_time(self):
        # Arrange
        token = "test_token"
        start_time = datetime.now()
        end_time = None

        # Insert the token watch record for the first time
        inserted_id = insert_token_watch(token, start_time, end_time)

        # New end_time to update the existing token watch record
        new_end_time = start_time + timedelta(hours=2)

        # Act: Set the new end time for the token
        set_end_time(token, new_end_time)

        # Retrieve the updated token watch record
        result = get_token_watch(token)

        # Assert: Verify that the end_time has been updated correctly
        self.assertIsNotNone(result, "Token watch should be retrievable from the database")
        self.assertEqual(result[0], inserted_id, "The inserted ID should match the result")
        self.assertEqual(result[3].isoformat(), new_end_time.isoformat(), "The end time should match the updated value")


from datetime import datetime

from database.token_creation_info_table import insert_token_creation_info
from tests.integration_tests.database.base_testdb import BaseTestDatabase


class TestRunner(BaseTestDatabase):

    def test_insert_token_creation_info(self):
        # Arrange
        token = "test_token"
        creator = "test_creator"
        timestamp = datetime.now()

        # Act: Insert the token creation info
        insert_token_creation_info(token, creator, timestamp)

        # Assert: Verify that the data was inserted into the database
        self.cursor.execute("""
            SELECT token, creator, timestamp
            FROM token_creation_info
        """)
        result = self.cursor.fetchone()

        self.assertIsNotNone(result, "The token creation info should be inserted into the database")
        self.assertEqual(result[0], token, "The token should match the inserted value")
        self.assertEqual(result[1], creator, "The creator should match the inserted value")
        self.assertEqual(result[2].isoformat(), timestamp.isoformat(), "The timestamp should match the inserted value")

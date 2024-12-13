from datetime import datetime

from database.token_creation_info_table import select_token_creation_info, insert_token_creation_info
from tests.integration_tests.database.base_testdb import BaseTestDatabase


class TestSelectTokenCreationInfo(BaseTestDatabase):

    def test_select_token_creation_info(self):
        # Arrange
        token = "test_token"
        creator = "test_creator"
        timestamp = datetime.now()

        # Insert the token creation info for testing
        insert_token_creation_info(token, creator, timestamp)

        # Act: Select the token creation info
        result = select_token_creation_info(token)

        # Assert: Verify that the correct token creation info is selected
        self.assertIsNotNone(result, "Token creation info should be retrievable from the database")
        self.assertEqual(result[0].isoformat(), timestamp.isoformat(), "The timestamp should match the inserted value")
        self.assertEqual(result[1], creator, "The creator should match the inserted value")

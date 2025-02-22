import pickle

from database.token_sample_table import insert_token_sample
from dto.token_sample_model import TokenSample
from tests.integration_tests.database.base_testdb import BaseTestDatabase


class TestInsertTokenSample(BaseTestDatabase):

    def test_insert_token_sample(self):
        # Arrange
        token = "test_token"
        raw_data = {"key": "value"}

        token_sample = TokenSample(
            token=token,
            raw_data=raw_data
        )

        # Act
        insert_token_sample(token_sample)

        # Assert
        self.cursor.execute("""
            SELECT token, raw
            FROM token_sample
        """)
        result = self.cursor.fetchone()

        self.assertIsNotNone(result, "The token sample should be inserted into the database")
        self.assertEqual(result[0], token, "The token should match the inserted value")

        # Unpickle the raw data to compare it with the original
        result_raw_data = pickle.loads(result[1])
        self.assertEqual(result_raw_data, raw_data, "The raw data should match the inserted value")

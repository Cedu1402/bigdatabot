import pickle
from datetime import datetime

from database.token_dataset_table import insert_token_dataset
from dto.token_dataset_model import TokenDataset
from tests.integration_tests.database.base_testdb import BaseTestDatabase


class TestRunner(BaseTestDatabase):

    def test_insert_token_dataset(self):
        # Arrange
        token = "test_token"
        trading_minute = datetime.now()
        raw_data = pickle.dumps({"key": "value"})  # Pickle the Python object

        token_dataset = TokenDataset(
            token=token,
            trading_minute=trading_minute,
            raw_data=raw_data
        )

        # Act
        insert_token_dataset(token_dataset)

        # Assert
        self.cursor.execute("""
            SELECT token, trading_minute, raw_data
            FROM token_dataset
        """)
        result = self.cursor.fetchone()

        self.assertIsNotNone(result, "The token dataset should be inserted into the database")
        self.assertEqual(result[0], token, "The token should match the inserted value")
        self.assertEqual(result[1].isoformat(), trading_minute.isoformat(),
                         "The trading minute should match the inserted value")

        # Unpickle the raw data to compare it with the original
        result_raw_data = pickle.loads(result[2])
        self.assertEqual(result_raw_data, {"key": "value"}, "The raw data should match the inserted value")

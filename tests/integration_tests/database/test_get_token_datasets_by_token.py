from datetime import datetime, timedelta

from database.token_dataset_table import get_token_datasets_by_token, insert_token_dataset
from dto.token_dataset_model import TokenDataset
from tests.integration_tests.database.base_testdb import BaseTestDatabase


class TestGetTokenDatasetsByToken(BaseTestDatabase):

    def test_get_token_datasets_by_token(self):
        # Arrange
        token = "test_token"
        trading_minute_1 = datetime.now() - timedelta(minutes=1)
        trading_minute_2 = datetime.now()

        raw_data_1 = {"price": 100, "volume": 50}
        raw_data_2 = {"price": 150, "volume": 75}

        # Create TokenDataset objects
        token_dataset_1 = TokenDataset(token=token, trading_minute=trading_minute_1, raw_data=raw_data_1)
        token_dataset_2 = TokenDataset(token=token, trading_minute=trading_minute_2, raw_data=raw_data_2)

        # Insert test data using the insert function
        insert_token_dataset(token_dataset_1)
        insert_token_dataset(token_dataset_2)

        # Act: Fetch the datasets
        result = get_token_datasets_by_token(token)

        # Assert: Verify the correct data is returned
        self.assertEqual(len(result), 2, "Should return exactly two datasets")

        # Check first dataset
        self.assertEqual(result[0].token, token, "Token should match for first dataset")
        self.assertEqual(result[0].trading_minute, trading_minute_1, "Trading minute should match for first dataset")
        self.assertEqual(result[0].raw_data, raw_data_1, "Raw data should match for first dataset")

        # Check second dataset
        self.assertEqual(result[1].token, token, "Token should match for second dataset")
        self.assertEqual(result[1].trading_minute, trading_minute_2, "Trading minute should match for second dataset")
        self.assertEqual(result[1].raw_data, raw_data_2, "Raw data should match for second dataset")

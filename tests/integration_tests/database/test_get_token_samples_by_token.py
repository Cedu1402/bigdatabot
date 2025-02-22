from database.token_sample_table import insert_token_sample, get_token_samples_by_token
from dto.token_sample_model import TokenSample
from tests.integration_tests.database.base_testdb import BaseTestDatabase


class TestGetTokenSamplesByToken(BaseTestDatabase):

    def test_get_token_samples_by_token(self):
        # Arrange
        token = "test_token"
        raw_data_1 = {"price": 100, "volume": 50}

        token_sample_1 = TokenSample(token=token, raw_data=raw_data_1)
        # Insert test data
        insert_token_sample(token_sample_1)

        # Act
        result = get_token_samples_by_token(token)

        # Assert
        self.assertEqual(result.token, token, "Token should match for first sample")
        self.assertEqual(result.raw_data, raw_data_1, "Raw data should match for first sample")

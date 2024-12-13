from datetime import datetime

from database.event_table import insert_event, signature_exists
from tests.integration_tests.database.base_testdb import BaseTestDatabase


class TestRunner(BaseTestDatabase):

    def test_signature_exists(self):
        # Arrange
        wallet = "test_wallet"
        time = datetime.now()
        signature = "unique_signature"

        # Insert the event for the first time
        insert_event(wallet, time, signature)

        # Act & Assert for "signature exists"
        exists = signature_exists(signature)
        self.assertTrue(exists, "The signature should exist in the database after being inserted")

    def test_signature_does_not_exist(self):
        # Arrange
        signature = "non_existing_signature"

        # Act & Assert for "signature does not exist"
        exists = signature_exists(signature)
        self.assertFalse(exists, "The signature should not exist in the database if it hasn't been inserted")

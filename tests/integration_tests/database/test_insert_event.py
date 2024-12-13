from datetime import datetime

from database.event_table import insert_event
from tests.integration_tests.database.base_testdb import BaseTestDatabase


class TestRunner(BaseTestDatabase):

    def test_insert_event(self):
        # Arrange
        wallet = "test_wallet"
        time = datetime.now()
        signature = "test_signature"

        # Act
        insert_event(wallet, time, signature)

        # Assert
        self.cursor.execute("""
                   SELECT wallet, time, signature 
                   FROM event 
                   WHERE wallet = %s AND signature = %s
               """, (wallet, signature))
        result = self.cursor.fetchone()

        self.assertIsNotNone(result, "The event should be inserted into the database")
        self.assertEqual(result[0], wallet, "The wallet should match the inserted value")
        self.assertEqual(result[1].isoformat(), time.isoformat(), "The time should match the inserted value")
        self.assertEqual(result[2], signature, "The signature should match the inserted value")

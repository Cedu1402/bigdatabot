from datetime import datetime, timedelta

from database.token_watch_table import get_current_token_watch_stats
from database.token_watch_table import insert_token_watch
from tests.integration_tests.database.base_testdb import BaseTestDatabase


class TestRunner(BaseTestDatabase):

    def test_get_current_token_watch_stats(self):
        # Arrange
        token1 = "test_token_1"
        token2 = "test_token_2"
        token3 = "test_token_3"
        now = datetime.now()

        # Insert tokens into the database
        insert_token_watch(token1, now, None)  # Currently watched
        insert_token_watch(token2, now - timedelta(days=1), now)  # Ended
        insert_token_watch(token3, now - timedelta(hours=1), None)  # Currently watched

        # Act
        stats = get_current_token_watch_stats()

        # Assert
        self.assertEqual(stats["total_watched"], 3, "The total watched count should be 3")
        self.assertEqual(stats["currently_watched"], 2, "The currently watched count should be 2")

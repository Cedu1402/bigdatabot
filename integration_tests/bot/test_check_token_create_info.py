import unittest
from unittest import mock
from datetime import datetime, timedelta
import json

from bot.event_worker import check_token_create_info
from constants import PUMP_DOT_FUN_AUTHORITY


# Mock `get_token_create_info` function
async def mock_get_token_create_info(token: str):
    # Define the token creation time and owner you want to mock
    token_create_time = datetime.utcnow() - timedelta(minutes=30)  # 30 minutes ago
    owner = "PUMP_DOT_FUN_AUTHORITY"  # Replace with expected authority
    return token_create_time, owner


class TestCheckTokenCreateInfo(unittest.IsolatedAsyncioTestCase):

    # Mock Redis Client
    @mock.patch('redis.asyncio.Redis')
    async def test_check_token_create_info_found(self, mock_redis):
        # Simulate a token create info already stored in Redis
        token = "mock_token_address"
        token_create_time = datetime.utcnow() - timedelta(minutes=30)
        owner = PUMP_DOT_FUN_AUTHORITY

        # Mock Redis get to return the stored data
        mock_redis_instance = mock_redis.return_value
        mock_redis_instance.get = mock.AsyncMock(return_value=json.dumps([token_create_time.isoformat(), owner]))

        # Call the function
        result = await check_token_create_info(mock_redis_instance, token)

        # Assert that the function returns True (since the token is valid and within 2 hours)
        self.assertTrue(result)

    # Test case for not a pump fun token
    @mock.patch('redis.asyncio.Redis')
    async def test_check_token_create_info_not_pump_fun(self, mock_redis):
        # Simulate a token that is not a "pump fun" token
        token = "mock_token_address"
        token_create_time = datetime.utcnow() - timedelta(minutes=30)
        owner = "Some_Other_Authority"

        # Mock Redis get to return the stored data
        mock_redis_instance = mock_redis.return_value
        mock_redis_instance.get = mock.AsyncMock(return_value=json.dumps([token_create_time.isoformat(), owner]))

        # Call the function
        result = await check_token_create_info(mock_redis_instance, token)

        # Assert that the function logs "Not a pump fun token" and returns False
        self.assertFalse(result)

    # Test case for token older than two hours
    @mock.patch('redis.asyncio.Redis')
    async def test_check_token_create_info_older_than_two_hours(self, mock_redis):
        # Simulate a token that is older than 2 hours
        token = "mock_token_address"
        token_create_time = datetime.utcnow() - timedelta(hours=3)  # 3 hours ago
        owner = PUMP_DOT_FUN_AUTHORITY

        # Mock Redis get to return the stored data
        mock_redis_instance = mock_redis.return_value
        mock_redis_instance.get = mock.AsyncMock(return_value=json.dumps([token_create_time.isoformat(), owner]))

        # Call the function
        result = await check_token_create_info(mock_redis_instance, token)

        # Assert that the function logs "Token older than two hours" and returns False
        self.assertFalse(result)

    # Test case for token not found in Redis
    @mock.patch('redis.asyncio.Redis')
    @mock.patch('bot.event_worker.load_token_create_info', new_callable=mock.AsyncMock)
    async def test_check_token_create_info_not_in_redis(self, mock_load, mock_redis):
        # Simulate a token that is not found in Redis, should call the external function to fetch data
        token = "mock_token_address"

        # Mock Redis get to return None (meaning it's not found)
        mock_redis_instance = mock_redis.return_value
        mock_redis_instance.get = mock.AsyncMock(return_value=None)

        # Mock the call to `load_token_create_info`
        mock_load.return_value = (datetime.utcnow() - timedelta(minutes=30), PUMP_DOT_FUN_AUTHORITY)

        # Call the function
        result = await check_token_create_info(mock_redis_instance, token)

        # Assert that the function returns True, as we mock `load_token_create_info` to return valid data
        self.assertTrue(result)

    # Helper function to mock an async function call
    def mock_async(self, coro):
        async def wrapper(*args, **kwargs):
            return await coro(*args, **kwargs)

        return wrapper


# Run the tests
if __name__ == '__main__':
    unittest.main()


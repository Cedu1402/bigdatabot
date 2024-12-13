import json
import unittest
from datetime import datetime
from unittest import mock
from unittest.mock import AsyncMock

from solders.pubkey import Pubkey

from bot.event_worker import handle_user_event
from bot.token_watcher import watch_token
from dto.trade_model import Trade


class TestHandleUserEvent(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.event_data = {
            "jsonrpc": "2.0",
            "method": "accountNotification",
            "params": {
                "result": {
                    "context": {"slot": 5199307},
                    "value": {
                        "data": [
                            "11116bv5nS2h3y12kD1yUKeMZvGcKLSjQgX6BeV7u1FrjeJcKfsHPXHRDEHrBesJhZyqnnq9qJeUuF7WHxiuLuL5twc38w2TXNLxnDbjmuR",
                            "base58"
                        ],
                        "executable": False,
                        "lamports": 33594,
                        "owner": "11111111111111111111111111111111",
                        "rentEpoch": 635,
                        "space": 80
                    }
                },
                "subscription": 23784
            }
        }

    @mock.patch('bot.event_worker.get_env_value')
    @mock.patch('bot.event_worker.get_async_redis')
    @mock.patch('bot.event_worker.get_sync_redis')
    @mock.patch('bot.event_worker.get_latest_user_trade')
    @mock.patch('bot.event_worker.check_token_create_info')
    @mock.patch('bot.event_worker.Queue')
    @mock.patch('bot.event_worker.token_watch_exists')
    @mock.patch('bot.event_worker.insert_trade')
    @mock.patch('bot.event_worker.insert_token_watch')
    @mock.patch('bot.event_worker.insert_event')
    async def test_handle_user_event_valid_trade(self, mock_insert_event, mock_insert_token_watch, mock_insert_trade,
                                                 mock_token_watch_exists, mock_queue,
                                                 mock_check_token_create_info,
                                                 mock_get_latest_user_trade, mock_get_sync_redis, mock_get_async_redis,
                                                 mock_get_env_value):
        # Mock Redis instance
        mock_redis = AsyncMock()
        mock_get_async_redis.return_value = mock_redis
        mock_get_sync_redis.return_value = mock_redis

        # Mock environment variables
        mock_get_env_value.return_value = "https://api.mainnet-beta.solana.com"

        # Mock trade data
        trader = "GWwmd3zZQnLvqvixKGD3RKtaFVAtfPn1kGN4bx8tHRTR"
        trade_data = Trade(trader, "testpump", 100, 1, True, 10, datetime.now().isoformat(), "test_sig")
        mock_get_latest_user_trade.return_value = trade_data

        # Mock check_token_create_info to always return True
        mock_check_token_create_info.return_value = True

        # Mock Queue and enqueue method
        mock_enqueue = mock.Mock()
        mock_queue.return_value.enqueue = mock_enqueue

        mock_token_watch_exists.return_value = False

        # Mock subscription_map
        subscription_map = {23784: trader}

        # Mock getting subscription map from Redis
        mock_redis.get.return_value = json.dumps(subscription_map)

        # Call the function
        await handle_user_event(json.dumps(self.event_data))

        # Ensure that the expected methods were called
        mock_get_latest_user_trade.assert_called_once_with(Pubkey.from_string(trader),
                                                           "https://api.mainnet-beta.solana.com")
        mock_check_token_create_info.assert_called_once_with("testpump")
        mock_queue.return_value.enqueue.assert_called_once_with(watch_token, "testpump")

        # Verify that the token was added to Redis
        mock_insert_trade.assert_called_once_with(trade_data)
        mock_insert_token_watch.assert_called_once()
        mock_insert_event.assert_called_once()

    @mock.patch('bot.event_worker.get_env_value')
    @mock.patch('bot.event_worker.get_async_redis')
    @mock.patch('bot.event_worker.get_sync_redis')
    @mock.patch('bot.event_worker.get_latest_user_trade')
    @mock.patch('bot.event_worker.insert_event')
    async def test_handle_user_event_no_trade(self, mock_insert_event, mock_get_latest_user_trade,
                                              mock_get_sync_redis, mock_get_async_redis, mock_get_env_value):
        # Mock Redis instance
        mock_redis = AsyncMock()
        mock_get_async_redis.return_value = mock_redis
        mock_get_sync_redis.return_value = mock_redis

        # Mock environment variables
        mock_get_env_value.return_value = "https://api.mainnet-beta.solana.com"

        # Mock trade data (None scenario)
        trader = "GWwmd3zZQnLvqvixKGD3RKtaFVAtfPn1kGN4bx8tHRTR"
        mock_get_latest_user_trade.return_value = None  # No trade found

        # Mock subscription_map
        subscription_map = {23784: trader}

        # Mock getting subscription map from Redis
        mock_redis.get.return_value = json.dumps(subscription_map)

        # Call the function
        await handle_user_event(json.dumps(self.event_data))

        # Ensure that no further Redis operations were made due to no trade being found
        mock_get_latest_user_trade.assert_called_once_with(Pubkey.from_string(trader),
                                                           "https://api.mainnet-beta.solana.com")
        mock_redis.lpush.assert_not_called()
        mock_insert_event.assert_called_once()

    @mock.patch('bot.event_worker.get_env_value')
    @mock.patch('bot.event_worker.get_async_redis')
    @mock.patch('bot.event_worker.get_sync_redis')
    @mock.patch('bot.event_worker.get_latest_user_trade')
    @mock.patch('bot.event_worker.check_token_create_info')
    @mock.patch('bot.event_worker.insert_event')
    @mock.patch('bot.event_worker.insert_token_watch')
    @mock.patch('bot.event_worker.token_watch_exists')
    @mock.patch('bot.event_worker.insert_trade')
    async def test_handle_user_event_token_already_exists(self, mock_insert_trade, mock_token_watch_exists,
                                                          mock_insert_token_watch, mock_insert_event,
                                                          mock_check_token_create_info,
                                                          mock_get_latest_user_trade,
                                                          mock_get_sync_redis, mock_get_async_redis,
                                                          mock_get_env_value):
        # Mock Redis instance
        mock_redis = AsyncMock()
        mock_get_async_redis.return_value = mock_redis
        mock_get_sync_redis.return_value = mock_redis

        # Mock environment variables
        mock_get_env_value.return_value = "https://api.mainnet-beta.solana.com"

        # Mock trade data
        trader = "GWwmd3zZQnLvqvixKGD3RKtaFVAtfPn1kGN4bx8tHRTR"
        trade_data = Trade(trader, "testpump", 100, 1, True, 10, datetime.now().isoformat(), "")
        mock_get_latest_user_trade.return_value = trade_data

        # Mock check_token_create_info to always return True
        mock_check_token_create_info.return_value = True

        # Mock subscription_map
        subscription_map = {23784: trader}

        # Mock getting subscription map from Redis
        mock_redis.get.return_value = json.dumps(subscription_map)

        # Mock that the token is already being watched
        mock_redis.exists.return_value = True

        # Call the function
        await handle_user_event(json.dumps(self.event_data))

        # Ensure that the token is not added again
        mock_insert_event.assert_called_once()
        mock_token_watch_exists.assert_called_once_with(trade_data.token)
        mock_insert_trade.assert_called_once_with(trade_data)
        mock_insert_token_watch.assert_not_called()

    @mock.patch('bot.event_worker.get_env_value')
    @mock.patch('bot.event_worker.get_async_redis')
    @mock.patch('bot.event_worker.get_sync_redis')
    @mock.patch('bot.event_worker.get_latest_user_trade')
    @mock.patch('bot.event_worker.check_token_create_info')
    @mock.patch('bot.event_worker.insert_event')
    @mock.patch('bot.event_worker.token_watch_exists')
    @mock.patch('bot.event_worker.insert_trade')
    async def test_handle_user_event_token_creation_check_fail(self, mock_insert_trade,
                                                               mock_token_watch_exists,
                                                               mock_insert_event, mock_check_token_create_info,
                                                               mock_get_latest_user_trade,
                                                               mock_get_sync_redis, mock_get_async_redis,
                                                               mock_get_env_value):
        # Mock Redis instance
        mock_redis = AsyncMock()
        mock_get_async_redis.return_value = mock_redis
        mock_get_sync_redis.return_value = mock_redis

        # Mock environment variables
        mock_get_env_value.return_value = "https://api.mainnet-beta.solana.com"

        # Mock trade data
        trader = "GWwmd3zZQnLvqvixKGD3RKtaFVAtfPn1kGN4bx8tHRTR"
        trade_data = Trade(trader, "testpump", 100, 1, True, 10, datetime.now().isoformat(), "")
        mock_get_latest_user_trade.return_value = trade_data

        # Mock check_token_create_info to return False (indicating a failed check)
        mock_check_token_create_info.return_value = False
        mock_token_watch_exists.return_value = True

        # Mock subscription_map
        subscription_map = {23784: trader}

        # Mock getting subscription map from Redis
        mock_redis.get.return_value = json.dumps(subscription_map)

        # Call the function
        await handle_user_event(json.dumps(self.event_data))

        # Ensure that token was not added due to creation check failure
        mock_redis.lpush.assert_not_called()
        mock_token_watch_exists.assert_called_once_with(trade_data.token)
        mock_insert_event.assert_called_once()
        mock_insert_trade.assert_not_called()


if __name__ == '__main__':
    unittest.main()

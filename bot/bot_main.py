import asyncio
import json
import logging
import os.path
from typing import List

import websockets
from dotenv import load_dotenv
from rq import Queue

from bot.event_worker import handle_user_event
from constants import SOLANA_WS, EVENT_QUEUE, BIN_AMOUNT_KEY, SUBSCRIPTION_MAP, ROOT_DIR
from data.redis_helper import get_sync_redis, get_async_redis
from database.raw_sql import run_sql_file
from env_data.get_env_value import get_env_value
from ml_model.decision_tree_model import DecisionTreeModel
from structure_log.logger_setup import setup_logger

subscription_map = {}

setup_logger("bot_main")
logger = logging.getLogger(__name__)


# Function to handle WebSocket messages
async def on_message(websocket):
    queue = Queue(EVENT_QUEUE, connection=get_sync_redis())

    while True:
        try:
            message = await websocket.recv()
            queue.enqueue(handle_user_event, message)
        except Exception as e:
            logger.exception("Failed to process message")
            break


# Function to subscribe to account changes via WebSocket
async def subscribe_to_accounts(websocket, traders: List[str]):
    for address in traders:
        subscription_message = {
            "jsonrpc": "2.0",
            "method": "accountSubscribe",
            "params": [address, {"encoding": "jsonParsed", "commitment": "finalized"}],
            "id": 1
        }
        await websocket.send(json.dumps(subscription_message))
        while True:
            response = await websocket.recv()
            response_data = json.loads(response)
            if "result" in response_data:
                subscription_id = response_data["result"]
                subscription_map[subscription_id] = address
                logger.info("Subscription mapped", extra={"subscription_id": subscription_id, "address": address})
                break


# Main function to handle WebSocket and Solana queries
async def main():
    ws_url = get_env_value(SOLANA_WS)
    config = dict()
    config[BIN_AMOUNT_KEY] = 10
    model = DecisionTreeModel(config)
    model.load_model("simple_tree")
    r = get_async_redis()
    traders = [column.replace("trader_", "").replace("_state", "") for column in model.get_columns() if
               "trader_" in column]
    traders.remove("Ad3AvvE3Qj7xf8sLh8vA34X7fqydhpsPrvEF3EZTwaki")

    retries = 0
    while True:
        try:
            async with websockets.connect(ws_url, max_size=200 ** 7) as websocket:
                logger.info("Connected to WebSocket")
                # Subscribe to accounts via WebSocket
                await subscribe_to_accounts(websocket, traders)
                # Handle incoming WebSocket messages
                await r.set(SUBSCRIPTION_MAP, json.dumps(subscription_map))
                await on_message(websocket)
        except Exception as e:
            logger.exception(f"Unexpected error. Retrying in {2 ** retries} seconds...")

        retries += 1
        await asyncio.sleep(min(30, 2 ** retries))


if __name__ == '__main__':
    load_dotenv()
    run_sql_file(os.path.join(ROOT_DIR, "database/tables.sql"))
    setup_logger("bot_main")
    # Run the event loop
    asyncio.run(main())

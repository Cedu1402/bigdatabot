import asyncio
import json
from typing import List

import websockets
from dotenv import load_dotenv
from loguru import logger
from rq import Queue

from bot.event_worker import handle_user_event
from constants import SOLANA_WS, EVENT_QUEUE, BIN_AMOUNT_KEY
from data.redis_helper import get_redis_client
from env_data.get_env_value import get_env_value
from ml_model.decision_tree_model import DecisionTreeModel

subscription_map = {}


# Function to handle WebSocket messages
async def on_message(websocket):
    r = get_redis_client()
    queue = Queue(EVENT_QUEUE, connection=r)

    while True:
        try:
            message = await websocket.recv()
            data = json.loads(message)
            logger.info("Received wallet action", data=data)
            queue.enqueue(handle_user_event, data)
        except Exception as e:
            logger.exception("Failed to process message")


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
                logger.info("Subscription mapped", subscription_id=subscription_id, address=address)
                break


# Main function to handle WebSocket and Solana queries
async def main():
    ws_url = get_env_value(SOLANA_WS)
    config = dict()
    config[BIN_AMOUNT_KEY] = 10
    model = DecisionTreeModel(config)
    model.load_model("simple_tree")

    traders = [column.replace("trader_", "").replace("_state", "") for column in model.get_columns() if
               "trader_" in column]

    async with websockets.connect(ws_url) as websocket:
        # Subscribe to accounts via WebSocket
        await subscribe_to_accounts(websocket, traders)

        # Handle incoming WebSocket messages
        await on_message(websocket)


if __name__ == '__main__':
    load_dotenv()
    # Run the event loop
    asyncio.run(main())

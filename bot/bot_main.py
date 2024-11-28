import asyncio
import json
import logging

import pandas as pd
import websockets
from dotenv import load_dotenv
from solana.rpc.api import Client
from solders.pubkey import Pubkey

from constants import SOLANA_WS
from data.solana_trader import get_trader_from_trades
from dune.data_collection import collect_all_data
from env_data.get_env_value import get_env_value
from solana_api.solana_data import get_user_trades_in_block

# Initialize Solana RPC client (using solana-py for basic queries)
client = Client("https://api.mainnet-beta.solana.com")
subscription_map = {}


# Function to handle WebSocket messages
async def on_message(websocket):
    while True:
        message = await websocket.recv()
        data = json.loads(message)
        logging.info(f"Received data: {data}")
        try:
            trader = subscription_map[data["params"]["subscription"]]
            logging.info(f"Received change for trader {trader}")
            slot = data["params"]["result"]["context"]["slot"]
            trades = await get_user_trades_in_block(Pubkey.from_string(trader), slot, "https://api.mainnet-beta.solana.com")
            if len(trades) > 0:
                logging.info(f"Trade found for trader {trader}")
        except Exception  as e:
            logging.error("Failed to process message", e)



# Function to subscribe to account changes via WebSocket
async def subscribe_to_accounts(websocket, traders: pd.DataFrame):
    for address in traders["trader"]:
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
                logging.info(f"Subscription ID {subscription_id} mapped to account {address}")
                break


# Main function to handle WebSocket and Solana queries
async def main():
    ws_url = get_env_value(SOLANA_WS)
    _, top_trader_trades = collect_all_data(True)
    traders = get_trader_from_trades(top_trader_trades)

    async with websockets.connect(ws_url) as websocket:
        # Subscribe to accounts via WebSocket
        await subscribe_to_accounts(websocket, traders)

        # Handle incoming WebSocket messages
        await on_message(websocket)


if __name__ == '__main__':
    load_dotenv()
    # Run the event loop
    asyncio.run(main())

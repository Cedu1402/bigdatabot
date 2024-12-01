import asyncio
from datetime import datetime, timedelta

import redis
from binance import AsyncClient, BinanceSocketManager

from constants import SOLANA_PRICE


async def main():
    client = await AsyncClient.create()
    # Set up the WebSocket manager
    bsm = BinanceSocketManager(client)
    r = redis.Redis()
    last_saved_time = datetime.utcnow() - timedelta(seconds=10)

    # Subscribe to the real-time SOL/USDT price stream
    stream = bsm.symbol_ticker_socket("SOLUSDT")
    # Start the WebSocket
    async with stream as ticker_stream:
        while True:
            msg = await ticker_stream.recv()  # Receive message
            if msg:
                price = msg['c']  # Extract the last price
                # Check if 10 seconds have passed since the last save
                now = datetime.utcnow()
                if (now - last_saved_time) >= timedelta(seconds=10):
                    await r.set(SOLANA_PRICE, str(price))  # Save to Redis
                    print("Price saved to Redis.")
                    print(f"Real-time SOL/USDT Price: {price}")
                    last_saved_time = now  # Update the last saved time


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

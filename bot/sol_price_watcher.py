import asyncio
from asyncio import sleep
from datetime import datetime, timedelta

from binance import AsyncClient, BinanceSocketManager
from dotenv import load_dotenv

from constants import SOLANA_PRICE
from data.redis_helper import get_async_redis
from structure_log.logger_setup import logger


async def main():
    load_dotenv()
    client = await AsyncClient.create()
    # Set up the WebSocket manager
    bsm = BinanceSocketManager(client)
    r = get_async_redis()
    last_saved_time = datetime.utcnow() - timedelta(seconds=10)

    # Subscribe to the real-time SOL/USDT price stream
    stream = bsm.symbol_ticker_socket("SOLUSDT")
    # Start the WebSocket
    async with stream as ticker_stream:
        while True:
            try:
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
            except Exception as e:
                logger.exception("Failed to get solana price")
                await sleep(10)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

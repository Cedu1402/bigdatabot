import asyncio
from asyncio import sleep

from dotenv import load_dotenv
from tabulate import tabulate

from constants import GLOBAL_PROFIT_KEY, GOOD_TRADES_KEY, BAD_TRADES_KEY, CURRENT_TRADE_WATCH_KEY, \
    CURRENT_TOKEN_WATCH_KEY, CURRENT_EVENT_WATCH_KEY, MAX_TRADE_WATCH_KEY, MAX_TOKEN_WATCH_KEY, MAX_EVENT_WATCH_KEY
from data.redis_helper import get_async_redis


async def update_maximums(r, current_key, max_key):
    """
    Updates the maximum value in Redis for a given key if the current value exceeds the stored maximum.

    :param r: Redis client
    :param current_key: Redis key for the current value
    :param max_key: Redis key for the maximum value
    """
    current_value = int(await r.get(current_key) or 0)
    max_value = int(await r.get(max_key) or 0)

    if current_value > max_value:
        await r.set(max_key, current_value)


async def main():
    r = get_async_redis()

    while True:
        global_return = await r.get(GLOBAL_PROFIT_KEY) or 0
        good_trades = await r.get(GOOD_TRADES_KEY) or 0
        bad_trades = await r.get(BAD_TRADES_KEY) or 0

        current_trades_watches = await r.get(CURRENT_TRADE_WATCH_KEY) or 0
        current_token_watches = await r.get(CURRENT_TOKEN_WATCH_KEY) or 0
        current_event_watches = await r.get(CURRENT_EVENT_WATCH_KEY) or 0

        max_trades = await r.get(MAX_TRADE_WATCH_KEY) or 0
        max_tokens = await r.get(MAX_TOKEN_WATCH_KEY) or 0
        max_events = await r.get(MAX_EVENT_WATCH_KEY) or 0

        # Update maximums for watches
        await update_maximums(r, CURRENT_TRADE_WATCH_KEY, MAX_TRADE_WATCH_KEY)
        await update_maximums(r, CURRENT_TOKEN_WATCH_KEY, MAX_TOKEN_WATCH_KEY)
        await update_maximums(r, CURRENT_EVENT_WATCH_KEY, MAX_EVENT_WATCH_KEY)

        # Prepare data for the table
        table_data = [
            ['Global Profit', int(global_return)],
            ['Good Trades', int(good_trades)],
            ['Bad Trades', int(bad_trades)],
            ['Current Trades Watches', int(current_trades_watches)],
            ['Max Trades Watches', int(max_trades)],
            ['Current Token Watches', int(current_token_watches)],
            ['Max Token Watches', int(max_tokens)],
            ['Current Event Watches', int(current_event_watches)],
            ['Max Event Watches', int(max_events)]
        ]

        # Print table in a formatted way
        print("\033c")  # Clears the terminal (works in most terminal environments)
        print(tabulate(table_data, headers=["Metric", "Value"], tablefmt="grid"))

        await sleep(2)

    pass


if __name__ == '__main__':
    load_dotenv()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

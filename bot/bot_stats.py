import asyncio
from asyncio import sleep

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
        global_return = await r.get(GLOBAL_PROFIT_KEY)
        good_trades = await r.get(GOOD_TRADES_KEY)
        bad_trades = await r.get(BAD_TRADES_KEY)

        current_trades_watches = await r.get(CURRENT_TRADE_WATCH_KEY)
        current_token_watches = await r.get(CURRENT_TOKEN_WATCH_KEY)
        current_event_watches = await r.get(CURRENT_EVENT_WATCH_KEY)

        max_trades = await r.get(MAX_TRADE_WATCH_KEY)
        max_tokens = await r.get(MAX_TOKEN_WATCH_KEY)
        max_events = await r.get(MAX_EVENT_WATCH_KEY)

        # Update maximums for watches
        await update_maximums(r, CURRENT_TRADE_WATCH_KEY, MAX_TRADE_WATCH_KEY)
        await update_maximums(r, CURRENT_TOKEN_WATCH_KEY, MAX_TOKEN_WATCH_KEY)
        await update_maximums(r, CURRENT_EVENT_WATCH_KEY, MAX_EVENT_WATCH_KEY)

        # Prepare data for the table
        table_data = [
            ['Global Profit', global_return],
            ['Good Trades', good_trades],
            ['Bad Trades', bad_trades],
            ['Current Trades Watches', current_trades_watches],
            ['Max Trades Watches', max_trades],
            ['Current Token Watches', current_token_watches],
            ['Max Token Watches', max_tokens],
            ['Current Event Watches', current_event_watches],
            ['Max Event Watches', max_events]
        ]

        # Print table in a formatted way
        print("\033c")  # Clears the terminal (works in most terminal environments)
        print(tabulate(table_data, headers=["Metric", "Value"], tablefmt="grid"))

        await sleep(2)

    pass


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

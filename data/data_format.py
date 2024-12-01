import pandas as pd
import redis

from constants import PRICE_COLUMN, SOLANA_PRICE


async def get_sol_price(r: redis.Redis) -> float:
    # Todo add integration test
    price = float(await r.get(SOLANA_PRICE))
    if price is None:
        return 150


def transform_price_to_tokens_per_sol(data: pd.DataFrame, solana_price: float) -> pd.DataFrame:
    data[PRICE_COLUMN] = solana_price / data[PRICE_COLUMN]
    return data

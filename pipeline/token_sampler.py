import asyncio

import pandas as pd
from flask.cli import load_dotenv

from constants import TOKEN_COlUMN, LAUNCH_DATE_COLUMN
from database.token_sample_table import insert_token_sample
from dto.token_sample_model import TokenSample
from dune.data_collection import get_close_volume_1m
from dune.dune_queries import get_token_sample


async def main(use_cache: bool):
    sampled = get_token_sample(use_cache)
    sampled = sampled.head(10)
    sampled[LAUNCH_DATE_COLUMN] = pd.to_datetime(sampled[LAUNCH_DATE_COLUMN])
    launch_times = sampled.set_index(TOKEN_COlUMN)[LAUNCH_DATE_COLUMN].to_dict()

    volume_close_1m = await get_close_volume_1m(list(sampled[TOKEN_COlUMN]),
                                                launch_times, use_cache, "SAMPLER")

    for token_data in volume_close_1m.groupby(TOKEN_COlUMN):
        insert_token_sample(TokenSample(str(token_data[0]), token_data[1]))


if __name__ == '__main__':
    load_dotenv()
    asyncio.run(main(True))

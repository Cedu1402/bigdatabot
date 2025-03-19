import asyncio

import pandas as pd
from flask.cli import load_dotenv

from constants import TOKEN_COLUMN, LAUNCH_DATE_COLUMN
from database.token_sample_table import insert_token_sample, get_token_samples_by_token
from dto.token_sample_model import TokenSample
from dune.data_collection import get_close_volume_1m
from dune.dune_queries import get_token_sample


async def main(use_cache: bool):
    sampled = get_token_sample(use_cache)
    # sampled = sampled.head(10)
    sampled[LAUNCH_DATE_COLUMN] = pd.to_datetime(sampled[LAUNCH_DATE_COLUMN])
    launch_times = sampled.set_index(TOKEN_COLUMN)[LAUNCH_DATE_COLUMN].to_dict()
    new_token_list = list()

    for token in list(sampled[TOKEN_COLUMN]):
        result = get_token_samples_by_token(token)
        if result is None:
            new_token_list.append(token)

    print(f"Total new tokens: {len(new_token_list)}")
    volume_close_1m = await get_close_volume_1m(new_token_list,
                                                launch_times, use_cache, "SAMPLER")

    for token_data in volume_close_1m.groupby(TOKEN_COLUMN):
        insert_token_sample(TokenSample(str(token_data[0]), token_data[1]))


if __name__ == '__main__':
    load_dotenv()
    asyncio.run(main(True))

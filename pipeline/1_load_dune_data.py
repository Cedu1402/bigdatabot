import asyncio
from typing import Tuple

import pandas as pd
from dotenv import load_dotenv

from dune.data_collection import collect_all_data


async def load_data(use_cache: bool) -> Tuple[pd.DataFrame, pd.DataFrame]:
    return await collect_all_data(use_cache)


if __name__ == '__main__':
    load_dotenv()
    use_cached_data = True
    asyncio.run(load_data(use_cached_data))

import json
import logging
from datetime import datetime, timedelta

import pandas as pd
import redis

from constants import CREATE_PREFIX, TRADE_PREFIX, BIN_AMOUNT_KEY
from ml_model.decision_tree_model import DecisionTreeModel


async def watch_token(token):
    # every minute check if we should buy
    r = redis.Redis()
    config = dict()
    config[BIN_AMOUNT_KEY] = 10
    model = DecisionTreeModel(config)
    model.load_model("simple_tree")

    while True:

        # check if coin is older than 4h if yes exit
        token_create_time = datetime.fromisoformat(r.get(CREATE_PREFIX + token))
        if (datetime.utcnow() - token_create_time).total_seconds() > 120 * 60:
            logging.info(f"Stop watch for token because of age {token}")
            return

        dataframe = pd.DataFrame()

        # get trades and prepare trader columns
        trades = await r.lrange(TRADE_PREFIX + token, 0, -1)
        trades = [json.loads(item) for item in trades]

        # get close and volume data


        # run data preparation

        # predict

        # start trading task and exit

    pass
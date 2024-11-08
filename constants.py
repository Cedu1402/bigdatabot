import os

SESSION = "mysession"
CHAT_ID = "chat_id"
TOPIC_ID = "topic_id"
DUNE_API_KEY = "DUNE_API_KEY"
TRAIN_VAL_TEST_FILE = "train_val_test"
RANDOM_SEED = 42

WIN_PERCENTAGE = 100
DRAW_DOWN_PERCENTAGE = 50

TRADE_LIST_QUERY = 4229277
TOP_TRADERS_QUERY = 4217799
TRADED_TOKENS_QUERY = 4229122
TOKEN_CLOSE_VOLUME_1M_QUERY = 4233197

PRICE_COLUMN = "latest_price"
PRICE_PCT_CHANGE = "price_pct_change"
TOTAL_VOLUME_PCT_CHANGE = "total_volume_pct_change"
SELL_VOLUME_PCT_CHANGE = "sell_volume_pct_change"
BUY_VOLUME_PCT_CHANGE = "buy_volume_pct_change"
TOKEN_COlUMN = "token"
TRADING_MINUTE_COLUMN = "trading_minute"
LABEL_COLUMN = "label"
BUY_VOLUME_COLUMN = 'buy_volume'
SELL_VOLUME_COLUMN = 'sell_volume'
TOTAL_VOLUME_COLUMN = 'total_volume'
SOL_PRICE = 150
MARKET_CAP_USD = 'market_cap_usd'
PERCENTAGE_OF_1_MILLION_MARKET_CAP = 'percentage_of_1_million_market_cap'

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_FOLDER = os.path.join(ROOT_DIR, "cache")

BIN_AMOUNT_KEY = "bin_amount"

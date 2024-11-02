import os

SESSION = "mysession"
CHAT_ID = "chat_id"
TOPIC_ID = "topic_id"
DUNE_API_KEY = "DUNE_API_KEY"

TRADE_LIST_QUERY = 4229277
TOP_TRADERS_QUERY = 4217799
TRADED_TOKENS_QUERY = 4229122
TOKEN_CLOSE_VOLUME_1M_QUERY = 4233197

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_FOLDER = os.path.join(ROOT_DIR, "cache")
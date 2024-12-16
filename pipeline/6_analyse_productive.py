from dotenv import load_dotenv

from constants import BIN_AMOUNT_KEY
from dune.top_trader_queries import get_list_of_traders
from ml_model.decision_tree_model import DecisionTreeModel


load_dotenv()
traders = get_list_of_traders(False)

config = dict()
config[BIN_AMOUNT_KEY] = 10
model = DecisionTreeModel(config)
model.load_model("simple_tree")

trader_columns = [trader.replace("trader_", "").replace("_state", "") for trader in model.get_columns() if "trader_" in trader]

for trader in trader_columns:
    if not (traders['trader_id'] == trader).any():
        print("Not found", trader)
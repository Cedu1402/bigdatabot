from dotenv import load_dotenv

from constants import BIN_AMOUNT_KEY
from data.dataset import prepare_validation_data, prepare_dataset
from data.solana_trader import get_trader_from_trades
from dune.data_collection import collect_all_data, collect_validation_data
from ml_model.decision_tree_model import DecisionTreeModel
from ml_model.model_evaluation import print_evaluation


def evaluate_model(use_cache: bool):
    config = dict()
    config[BIN_AMOUNT_KEY] = 10
    model = DecisionTreeModel(config)
    model.load_model("simple_tree")

    # load current data
    validation_data = prepare_validation_data(use_cache, model.get_columns())
    validation_x, validation_y = model.prepare_prediction_data(validation_data, True)

    # predict
    prediction = model.predict(validation_x)

    # calculate scores
    print_evaluation(validation_y, prediction)

    # calculate return 1 token only one trade
    start_balance = 50


if __name__ == '__main__':
    load_dotenv()
    use_cached_data = True
    evaluate_model(use_cache=use_cached_data)

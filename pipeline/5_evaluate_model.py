from dotenv import load_dotenv

from data.dataset import prepare_validation_data
from ml_model.decision_tree_model import DecisionTreeModel
from ml_model.model_evaluation import print_evaluation


def evaluate_model(use_cached: bool):
    model = DecisionTreeModel(dict())
    model.load_model("simple_tree")

    # load current data
    validation_data = prepare_validation_data(use_cached)
    validation_x, validation_y, _, _, _, _ = model.prepare_data(validation_data, None, None)

    # predict
    prediction = model.predict(validation_x)

    # calculate scores
    print_evaluation(validation_y, prediction)

    # calculate return 1 token only one trade
    start_balance = 50




if __name__ == '__main__':
    load_dotenv()
    use_cached_data = True
    evaluate_model(use_cached=use_cached_data)

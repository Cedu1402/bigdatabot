import copy

from dotenv import load_dotenv

from config.config_reader import load_yaml_to_dict
from constants import BIN_AMOUNT_KEY, CONFIG_2_FILE
from data.dataset import prepare_test_data
from ml_model.decision_tree_model import DecisionTreeModel


def main():
    load_dotenv()
    token = "96bTXQUtjPYuJoU5vK3w63qXn8Csgzad7JSW1qmUpump"
    config = dict()
    config[BIN_AMOUNT_KEY] = 10
    model = DecisionTreeModel(config)
    model.load_model("simple_tree")
    data_config = load_yaml_to_dict(CONFIG_2_FILE)
    test_data = prepare_test_data(token, True, model.get_columns(), data_config)
    validation_x, _ = model.prepare_prediction_data(copy.deepcopy(test_data), False)








if __name__ == '__main__':
    main()

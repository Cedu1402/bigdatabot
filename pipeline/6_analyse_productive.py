import copy

import numpy as np
from dotenv import load_dotenv

from config.config_reader import load_yaml_to_dict
from constants import BIN_AMOUNT_KEY, CONFIG_2_FILE
from data.dataset import prepare_test_data
from database.token_dataset_table import get_token_datasets_by_token
from ml_model.decision_tree_model import DecisionTreeModel


def main():
    load_dotenv()
    token = "7woyyqRRSNr7gtqxY5iXg9mzEC7hAjiLtxSmkAUypump"
    config = dict()
    config[BIN_AMOUNT_KEY] = 10
    model = DecisionTreeModel(config)
    model.load_model("simple_tree")
    data_config = load_yaml_to_dict(CONFIG_2_FILE)
    test_data = prepare_test_data(token, True, model.get_columns(), data_config)
    validation_x, _ = model.prepare_prediction_data(copy.deepcopy(test_data), False)
    predictions = model.predict(validation_x)
    print(np.any(predictions))


    prod_data = get_token_datasets_by_token(token)
    pass





if __name__ == '__main__':
    main()

from dotenv import load_dotenv

from constants import BIN_AMOUNT_KEY, RANDOM_SEED
from data.dataset import prepare_dataset
from data.random_seed import set_random_seed
from ml_model.decision_tree_model import DecisionTreeModel


def train_model(use_cache: bool):
    train, val, test = prepare_dataset(use_cache)
    config = dict()
    config[BIN_AMOUNT_KEY]  = 50
    model = DecisionTreeModel(config)
    train_x, train_y, val_x, val_y, test_x, test_y = model.prepare_data(train, val, test)
    model.build_model()
    model.train(train_x, train_y, val_x, val_y)
    model.save()


if __name__ == '__main__':
    load_dotenv()
    set_random_seed(RANDOM_SEED)
    use_cached_data = True
    train_model(use_cached_data)

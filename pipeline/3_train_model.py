from dotenv import load_dotenv

from data.dataset import prepare_dataset
from ml_model.decision_tree_model import DecisionTreeModel


def train_model(use_cache: bool):
    train, val, test = prepare_dataset(use_cache)
    model = DecisionTreeModel()
    model.prepare_data(train, val, test)
    pass


if __name__ == '__main__':
    load_dotenv()
    use_cached_data = True
    train_model(use_cached_data)

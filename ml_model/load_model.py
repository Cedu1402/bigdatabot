import os

from constants import MODEL_FOLDER
from data.pickle_files import load_from_pickle
from ml_model.base_model import BaseModelBuilder


def load_model(model_name: str) -> BaseModelBuilder:
    return load_from_pickle(os.path.join(MODEL_FOLDER, model_name + ".pkl"))
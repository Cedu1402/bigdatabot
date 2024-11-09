import os

from constants import MODEL_FOLDER
from data.pickle_files import load_from_pickle
from ml_model.base_model import BaseModel


def load_model(model_name: str) -> BaseModel:
    return load_from_pickle(os.path.join(MODEL_FOLDER, model_name + ".pkl"))
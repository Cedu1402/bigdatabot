import random


class InfoSet:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'info_sets'):
            self.info_sets = None
            self.current_info_set = None

    def set_info_set(self, info_sets):
        self.info_sets = info_sets

    def set_random_info_set(self):
        if not self.info_sets:
            raise ValueError("InfoSets not set.")
        self.current_info_set = random.choice(self.info_sets)

    def get_info_set(self):
        if self.current_info_set is None:
            raise ValueError('InfoSet.current_info_set is None')

        return self.current_info_set

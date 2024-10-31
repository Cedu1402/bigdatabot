import os


def get_api_key():
    return os.getenv('BIRDEYE_KEY')
import os
from typing import Optional


def get_env_value(key: str) -> Optional[str]:
    return os.environ.get(key)
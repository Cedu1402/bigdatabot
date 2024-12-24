import os
from typing import Optional


def get_env_value(key: str) -> Optional[str]:
    return os.environ.get(key)


def parse_bool(value: str) -> bool:
    return value.lower() == 'true'


def get_env_bool_value(key: str) -> Optional[bool]:
    value = os.environ.get(key)
    if value is None:
        return False

    return parse_bool(value)

from dataclasses import dataclass
from typing import Any


@dataclass
class TokenSample:
    token: str
    raw_data: Any

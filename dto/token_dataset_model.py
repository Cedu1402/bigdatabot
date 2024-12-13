from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Any


@dataclass
class TokenDataset:
    token: str
    trading_minute: datetime
    raw_data: Any
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class TokenTradeHistory:
    token: str
    buy_time: datetime
    sell_time: Optional[datetime]
    buy_price: float
    sell_price: Optional[float]

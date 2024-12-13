from dataclasses import dataclass
from datetime import datetime


@dataclass
class TokenTradeHistory:
    token: str
    buy_time: datetime
    sell_time: datetime
    buy_price: float
    sell_price: float

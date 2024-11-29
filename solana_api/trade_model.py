from dataclasses import dataclass
from datetime import datetime


@dataclass
class Trade:
    trader: str
    token: str
    token_amount: float
    sol_amount: float
    buy: bool
    token_holding_after: float
    time: datetime

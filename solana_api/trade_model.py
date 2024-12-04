from dataclasses import dataclass, asdict
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

    def __iter__(self):
        data = asdict(self)
        data["time"] = self.time.isoformat()  # Convert datetime to string
        return iter(data.items())

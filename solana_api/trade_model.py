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
    trade_time: str

    def get_time(self) -> datetime:
        return datetime.fromisoformat(self.trade_time)

    def to_dict(self):
        trade_dict = asdict(self)
        return trade_dict

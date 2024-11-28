from dataclasses import dataclass


@dataclass
class Trade:
    token: str
    token_amount: float
    sol_amount: float
    buy: bool
    token_holding_after: float

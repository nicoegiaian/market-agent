from pydantic import BaseModel
from datetime import datetime
from typing import Literal

class Bar(BaseModel):
    instrument_id: str
    provider: str
    timeframe: Literal["1m","5m","1d"]
    ts: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float | None = None
    currency: str = "ARS"

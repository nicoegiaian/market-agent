from pydantic import BaseModel
from datetime import datetime
from typing import Literal

class Signal(BaseModel):
    instrument_id: str
    rule_id: str
    ts: datetime
    direction: Literal["buy","sell","watch"]
    score: float
    reason: str
    details: dict

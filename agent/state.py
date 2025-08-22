from datetime import datetime
from typing import List
from models.signals import Signal

LAST_TICK: datetime | None = None
LAST_SIGNALS: List[Signal] = []

def set_last_tick(ts: datetime) -> None:
    global LAST_TICK; LAST_TICK = ts

def set_signals(signals: List[Signal]) -> None:
    global LAST_SIGNALS; LAST_SIGNALS = signals

def get_status() -> dict:
    return {
        "last_tick": LAST_TICK.isoformat() if LAST_TICK else None,
        "signals_count": len(LAST_SIGNALS)
    }

def get_signals_dict() -> list[dict]:
    return [s.model_dump() for s in LAST_SIGNALS]


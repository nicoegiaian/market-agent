from typing import Iterable
from models import Signal

class ConsoleNotifier:
    async def send(self, signals: Iterable[Signal]):
        for s in signals:
            print(f"[ALERTA] {s.instrument_id} {s.direction} score={s.score:.2f} — {s.reason}")

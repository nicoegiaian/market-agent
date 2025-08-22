import asyncio
from datetime import datetime
from typing import Iterable, List
import yfinance as yf
from models import Bar, Instrument

INTERVALS = [
    ("1m",  "5d"),   # si no hay 1m,…
    ("5m",  "5d"),
    ("15m", "10d"),
    ("1d",  "1mo"),  # fallback robusto (diario)
]

class YFPrices:
    async def fetch_bars(self, instruments: Iterable[Instrument], timeframe: str = "1d") -> List[Bar]:
        out: List[Bar] = []
        loop = asyncio.get_event_loop()
        tasks = [loop.run_in_executor(None, self._fetch_many, inst) for inst in instruments]
        for res in await asyncio.gather(*tasks, return_exceptions=True):
            if isinstance(res, list): out.extend(res)
        return out

    def _fetch_many(self, inst: Instrument) -> list[Bar]:
        for interval, period in INTERVALS:
            try:
                hist = yf.Ticker(inst.symbol).history(period=period, interval=interval, auto_adjust=False, prepost=False)
                if hist is None or hist.empty:
                    continue
                bars: list[Bar] = []
                for ts, row in hist.tail(60).iterrows():  # últimas ~60
                    dt = ts.to_pydatetime() if hasattr(ts, "to_pydatetime") else datetime.utcnow()
                    bars.append(Bar(
                        instrument_id=inst.instrument_id,
                        provider="yfinance",
                        timeframe=interval,
                        ts=dt,
                        open=float(row.get("Open", 0.0)),
                        high=float(row.get("High", 0.0)),
                        low=float(row.get("Low", 0.0)),
                        close=float(row.get("Close", 0.0)),
                        volume=float(row.get("Volume", 0.0)),
                        currency=inst.currency or "ARS",
                    ))
                if bars:
                    return bars
            except Exception:
                continue
        return []  # si todo falló, devolvé vacío sin romper


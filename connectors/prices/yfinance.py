# connectors/prices/yfinance.py
import asyncio
from datetime import datetime
from typing import Iterable, List
import requests
import yfinance as yf
from models import Bar, Instrument

# Probar varios intervalos/periodos; si intradía falla, caer a diario.
INTERVALS = [
    ("1m",  "5d"),
    ("5m",  "5d"),
    ("15m", "10d"),
    ("1d",  "1mo"),
]

# Deep-fallback si todo lo anterior falla
DAILY_FALLBACK_PERIODS = ["3mo", "6mo", "1y", "5y", "max"]

def _session() -> requests.Session:
    s = requests.Session()
    # Algunos edges de Yahoo bloquean UA por defecto
    s.headers.update({"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                                    "(KHTML, like Gecko) Chrome/115 Safari/537.36"})
    return s

class YFPrices:
    async def fetch_bars(self, instruments: Iterable[Instrument], timeframe: str = "1d") -> List[Bar]:
        out: List[Bar] = []
        loop = asyncio.get_event_loop()
        tasks = [loop.run_in_executor(None, self._fetch_many, inst) for inst in instruments]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for res in results:
            if isinstance(res, list):
                out.extend(res)
        return out

    def _fetch_many(self, inst: Instrument) -> list[Bar]:
        s = _session()
        t = yf.Ticker(inst.symbol, session=s)

        # 1) Intentos “normales”
        for interval, period in INTERVALS:
            try:
                hist = t.history(period=period, interval=interval, auto_adjust=False, prepost=False)
                if hist is not None and not hist.empty:
                    return self._to_bars(hist, inst, interval)
            except Exception:
                continue

        # 2) Deep fallback: diario con periodos largos
        for period in DAILY_FALLBACK_PERIODS:
            try:
                hist = t.history(period=period, interval="1d", auto_adjust=False, prepost=False)
                if hist is not None and not hist.empty:
                    return self._to_bars(hist, inst, "1d")
            except Exception:
                continue

        # 3) Último recurso: nada
        return []

    def _to_bars(self, hist, inst: Instrument, timeframe: str) -> list[Bar]:
        bars: list[Bar] = []
        # Tomá las últimas ~60 entries
        for ts, row in hist.tail(60).iterrows():
            dt = ts.to_pydatetime() if hasattr(ts, "to_pydatetime") else datetime.utcnow()
            bars.append(Bar(
                instrument_id=inst.instrument_id,
                provider="yfinance",
                timeframe=timeframe,
                ts=dt,
                open=float(row.get("Open", 0.0)),
                high=float(row.get("High", 0.0)),
                low=float(row.get("Low", 0.0)),
                close=float(row.get("Close", 0.0)),
                volume=float(row.get("Volume", 0.0)),
                currency=inst.currency or "ARS",
            ))
        return bars


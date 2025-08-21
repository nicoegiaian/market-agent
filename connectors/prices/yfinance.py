import asyncio
from datetime import datetime
from typing import Iterable, List
import yfinance as yf
from models import Bar, Instrument

class YFPrices:
    async def fetch_bars(self, instruments: Iterable[Instrument], timeframe: str = "1d") -> List[Bar]:
        out: List[Bar] = []
        loop = asyncio.get_event_loop()
        tasks = []
        for inst in instruments:
            tasks.append(loop.run_in_executor(None, self._fetch_one, inst, timeframe))
        for res in await asyncio.gather(*tasks, return_exceptions=True):
            if isinstance(res, Bar):
                out.append(res)
        return out

    def _fetch_one(self, inst: Instrument, timeframe: str) -> Bar | None:
        try:
            hist = yf.Ticker(inst.symbol).history(period="1d", interval="1m" if timeframe=="1m" else "1d")
            if hist.empty:
                return None
            last = hist.iloc[-1]
            ts = last.name.to_pydatetime() if hasattr(last.name, 'to_pydatetime') else datetime.utcnow()
            return Bar(
                instrument_id=inst.instrument_id,
                provider="yfinance",
                timeframe=timeframe,
                ts=ts,
                open=float(last.get("Open", last.get("open", 0.0))),
                high=float(last.get("High", last.get("high", 0.0))),
                low=float(last.get("Low", last.get("low", 0.0))),
                close=float(last.get("Close", last.get("close", 0.0))),
                volume=float(last.get("Volume", 0.0)),
                currency=inst.currency or "ARS",
            )
        except Exception:
            return None

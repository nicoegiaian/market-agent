import os
from datetime import datetime, timedelta, UTC
from typing import List
import httpx
from models import Bar, Instrument

TIINGO_TOKEN = os.getenv("TIINGO_API_KEY", "").strip()

async def fetch_daily(inst: Instrument, days: int = 90) -> List[Bar]:
    """
    Trae velas diarias EOD desde Tiingo para un ticker (ej.: AAPL).
    Retorna como List[Bar] (máx. ~60 últimas barras).
    """
    if not TIINGO_TOKEN:
        return []
    start = (datetime.now(UTC) - timedelta(days=days)).date().isoformat()
    url = f"https://api.tiingo.com/tiingo/daily/{inst.symbol}/prices"
    params = {"startDate": start, "resampleFreq": "daily", "token": TIINGO_TOKEN}
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.get(url, params=params)
        r.raise_for_status()
        data = r.json()
    bars: List[Bar] = []
    for row in data[-60:]:
        # Tiingo devuelve "date": "2025-08-21T00:00:00+00:00"
        dt = datetime.fromisoformat(row["date"].replace("Z", "+00:00"))
        bars.append(Bar(
            instrument_id=inst.instrument_id,
            provider="tiingo",
            timeframe="1d",
            ts=dt,
            open=float(row["open"]),
            high=float(row["high"]),
            low=float(row["low"]),
            close=float(row["close"]),
            volume=float(row.get("volume") or 0.0),
            currency=inst.currency or "USD",
        ))
    return bars


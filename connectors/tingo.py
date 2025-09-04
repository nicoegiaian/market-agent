# connectors/tingo.py
import os, time, requests
from functools import lru_cache
from typing import Literal, Dict, Any

TINGO_API_KEY = os.getenv("TIINGO_API_KEY")
BASE = "https://api.tiingo.com/tiingo"

class TingoError(Exception): ...

def _auth_params():
    if not TINGO_API_KEY:
        raise TingoError("Missing TINGO_API_KEY")
    return {"token": TINGO_API_KEY}

# Simple cache para no matar la API
def _tskey(symbol: str, start: str, end: str, interval: str) -> str:
    return f"{symbol}:{start}:{end}:{interval}"

_cache: Dict[str, Any] = {}
_TTL = 60  # segundos

def _get(url: str, params: Dict[str, Any]) -> Any:
    r = requests.get(url, params=params, timeout=20)
    if r.status_code >= 400:
        raise TingoError(f"HTTP {r.status_code}: {r.text[:200]}")
    return r.json()

Ranges = Literal["1d", "5d", "1mo", "3mo", "6mo", "ytd", "1y"]
Intervals = Literal["1min","5min","15min","1hour","4hour","1day"]

def _range_to_dates(range_: str) -> tuple[str, str]:
    # Muy simple (server en UTC); si ya usás rangos con fechas exactas, podés ignorar esto.
    from datetime import datetime, timedelta, timezone
    now = datetime.now(timezone.utc)
    mapping = {
        "1d": 1, "5d": 5, "1mo": 30, "3mo": 90, "6mo": 180, "ytd": (now - datetime(now.year,1,1,tzinfo=timezone.utc)).days or 1, "1y": 365
    }
    days = mapping.get(range_, 5)
    start = (now - timedelta(days=days)).date().isoformat()
    end = now.date().isoformat()
    return start, end

def get_prices(symbol: str, range_: Ranges = "5d", interval: Intervals = "5min"):
    start, end = _range_to_dates(range_)
    key = _tskey(symbol.upper(), start, end, interval)
    hit = _cache.get(key)
    now = time.time()
    if hit and now - hit["ts"] < _TTL:
        return hit["data"]

    # Tiingo IEX intraday/historical (equities/ETFs). Si usás Crypto/FX, crea funciones hermanas.
    url = f"{BASE}/iex/{symbol}/prices"
    params = {
        **_auth_params(),
        "startDate": start,
        "endDate": end,
        "resampleFreq": interval,  # p.ej. 5min/15min/1day
        "columns": "open,high,low,close,volume,date"
    }
    data = _get(url, params)
    # Normalizamos a lo que el front ya espera
    out = [
        {
            "t": p["date"],            # ISO datetime
            "o": p.get("open"),
            "h": p.get("high"),
            "l": p.get("low"),
            "c": p.get("close"),
            "v": p.get("volume"),
        }
        for p in data
        if p.get("close") is not None
    ]
    _cache[key] = {"ts": now, "data": out}
    return out

def get_quote(symbol: str):
    # Último precio para mostrar “Last / Change”
    url = f"{BASE}/iex/{symbol}"
    data = _get(url, _auth_params())
    # Respuesta es lista con un objeto por símbolo
    if isinstance(data, list) and data:
        d = data[0]
    else:
        d = data
    return {
        "symbol": d.get("ticker", symbol.upper()),
        "last": d.get("last") or d.get("tngoLast") or d.get("prevClose"),
        "prevClose": d.get("prevClose"),
        "ts": d.get("quoteTimestamp")
    }

def list_instruments():
    # Si tenés catálogo propio en DB, devolver desde ahí.
    # Provisorio: hardcode / o leer de env/archivo
    return [
        {"symbol": "AAPL", "name": "Apple Inc."},
        {"symbol": "MSFT", "name": "Microsoft"},
        {"symbol": "SPY", "name": "SPDR S&P 500 ETF"},
        # agrega los tuyos...
    ]


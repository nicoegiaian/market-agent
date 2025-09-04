# routers/prices.py
from fastapi import APIRouter, HTTPException, Query
from connectors.tingo import get_prices, get_quote, TingoError

router = APIRouter(prefix="/prices", tags=["prices"])

@router.get("")
def prices(
    symbol: str = Query(..., description="Ticker, ej: AAPL"),
    range: str = Query("5d", description="1d|5d|1mo|3mo|6mo|ytd|1y"),
    interval: str = Query("5min", description="1min|5min|15min|1hour|4hour|1day"),
):
    try:
        series = get_prices(symbol, range, interval)
        quote = get_quote(symbol)
        return {"symbol": symbol.upper(), "series": series, "quote": quote}
    except TingoError as e:
        raise HTTPException(status_code=502, detail=str(e))


from fastapi import HTTPException, Query
from normalize.instruments import load_instruments
from connectors.prices.tiingo import fetch_daily as tiingo_fetch_daily
# (podés dejar yfinance como opcional si querés, pero no lo usaremos en el “happy path”)

@app.get("/prices")
async def prices(
    instrument_id: str = Query(..., description="ID definido en instruments.yaml"),
    points: int = Query(60, ge=10, le=400),
    provider: str = Query("auto", pattern="^(auto|tiingo|yfinance)$")
):
    insts = load_instruments()
    match = next((i for i in insts if i.instrument_id == instrument_id), None)
    if not match:
        raise HTTPException(status_code=404, detail="instrument_id not found")

    bars = []

    # Happy path: Tiingo si la fuente del instrumento lo indica o si lo fuerzo por query
    if provider in ("auto", "tiingo") and (match.source == "tiingo" or provider == "tiingo"):
        bars = await tiingo_fetch_daily(match)

    # (Opcional) fallback a yfinance solo si lo pedís explícitamente por query
    # if not bars and provider == "yfinance":
    #     from connectors.prices.yfinance import YFPrices
    #     yf = YFPrices()
    #     try:
    #         bars_all = await yf.fetch_bars([match], timeframe="1d")
    #     except TypeError:
    #         bars_all = yf._fetch_many(match)
    #     bars = [b for b in bars_all if getattr(b, "instrument_id", None) == instrument_id]

    series = [{"t": b.ts.isoformat(), "c": b.close} for b in bars[-points:]] if bars else []
    return {"instrument_id": instrument_id, "series": series, "provider": bars[0].provider if bars else provider}


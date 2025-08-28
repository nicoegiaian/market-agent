import os, pytest
from models import Instrument
from connectors.prices.tiingo import fetch_daily

@pytest.mark.skipif(not os.getenv("TIINGO_API_KEY"), reason="TIINGO_API_KEY not set")
@pytest.mark.asyncio
async def test_tiingo_fetch_daily_returns_bars_for_aapl():
    inst = Instrument(symbol="AAPL", instrument_id="AAPL_US", type="equity", currency="USD", source="tiingo")
    bars = await fetch_daily(inst, days=60)
    assert len(bars) > 0, "Tiingo should return at least 1 daily bar for AAPL"
    for b in bars:
        assert b.instrument_id == "AAPL_US"
        assert b.close > 0


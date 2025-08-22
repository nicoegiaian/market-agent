import os, yaml
from fastapi import FastAPI, HTTPException, BackgroundTasks, Header, Query
from pydantic import BaseModel
from pathlib import Path
from normalize.instruments import load_instruments, save_instruments
from fastapi.middleware.cors import CORSMiddleware
from agent.main import load_rules, tick as agent_tick
from agent.state import get_status, get_signals_dict
from connectors.prices.yfinance import YFPrices




app = FastAPI(title="Market Agent API")

# CORS (permití Vercel)
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https://.*vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

origins = os.getenv("CORS_ALLOWED_ORIGINS", "").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o for o in origins if o],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

AGENT_TOKEN = os.getenv("AGENT_TOKEN", "")  # setéalo en Render


class NewInstrument(BaseModel):
    symbol: str
    instrument_id: str
    type: str
    currency: str = "ARS"
    source: str = "yfinance"

@app.get("/status")
async def status():
    return get_status()

@app.get("/signals")
async def signals():
    return get_signals_dict()

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

@app.get("/rules")
async def get_rules():
    cfg = yaml.safe_load(Path("config/rules.yaml").read_text())
    return cfg

@app.post("/instruments")
async def add_instrument(body: NewInstrument):
    items = load_instruments()
    if any(i.instrument_id == body.instrument_id for i in items):
        raise HTTPException(status_code=400, detail="instrument_id already exists")
    items.append(body)  # Pydantic model is compatible with our save function
    save_instruments(items)
    return [i.model_dump() for i in load_instruments()]


# NUEVO: dispara un ciclo del agente y vuelve enseguida
@app.post("/run-tick")
async def run_tick(background: BackgroundTasks, authorization: str | None = Header(None)):
    if AGENT_TOKEN and authorization != f"Bearer {AGENT_TOKEN}":
        raise HTTPException(status_code=401, detail="Unauthorized")
    async def _run():
        rules = await load_rules()
        await agent_tick(rules)     # un ciclo: ingesta -> señales -> notificaciones
    background.add_task(_run)
    return {"ok": True}

@app.get("/prices")
async def prices(instrument_id: str = Query(..., description="ID del instrumento definido en instruments.yaml"),
                 points: int = Query(60, ge=10, le=400)):
    # Busca el instrumento por ID, trae ~N cierres (con fallback 1d si intradía falla)
    insts = load_instruments()
    match = next((i for i in insts if i.instrument_id == instrument_id), None)
    if not match:
        raise HTTPException(status_code=404, detail="instrument_id not found")
    yf = YFPrices()
    bars = await yf._fetch_many(match)  # usa el método que ya trae ~60 barras con fallback
    if not bars:
        return {"instrument_id": instrument_id, "series": []}
    series = [{"t": b.ts.isoformat(), "c": b.close} for b in bars[-points:]]
    return {"instrument_id": instrument_id, "series": series}

# api/app.py
import os, yaml
from pathlib import Path
from fastapi import FastAPI, HTTPException, BackgroundTasks, Header, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# --- imports de tu proyecto ---
from normalize.instruments import load_instruments, save_instruments
from agent.main import load_rules, tick as agent_tick
from agent.state import get_status, get_signals_dict

# Proveedores de precios
from connectors.prices.tiingo import fetch_daily as tiingo_fetch_daily
from connectors.prices.yfinance import YFPrices

# ===== 1) Instancia de FastAPI (debe ir ANTES de usar @app.get) =====
app = FastAPI(title="Market Agent API")

# ===== 2) CORS (un solo middleware) =====
list_origins = [o.strip() for o in os.getenv("CORS_ALLOWED_ORIGINS", "").split(",") if o.strip()]
regex = os.getenv("CORS_ALLOWED_REGEX")  # ej: r"https://.*\.vercel\.app"
app.add_middleware(
    CORSMiddleware,
    allow_origins=list_origins,          # ej: http://localhost:5173
    allow_origin_regex=regex,            # ej: todos los previews de Vercel
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],                 # Authorization, Content-Type, etc.
)

AGENT_TOKEN = os.getenv("AGENT_TOKEN", "").strip()

# ===== 3) Endpoints =====

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

@app.get("/rules")
async def get_rules():
    path = Path("config/rules.yaml")
    return yaml.safe_load(path.read_text()) if path.exists() else []

class NewInstrument(BaseModel):
    symbol: str
    instrument_id: str
    type: str
    currency: str = "ARS"
    source: str = "yfinance"

@app.get("/instruments")
async def list_instruments():
    return [i.model_dump() for i in load_instruments()]

@app.post("/instruments")
async def add_instrument(body: NewInstrument):
    items = load_instruments()
    if any(i.instrument_id == body.instrument_id for i in items):
        raise HTTPException(status_code=400, detail="instrument_id already exists")
    items.append(body)  # Pydantic model compatible con save
    save_instruments(items)
    return {"ok": True}

@app.get("/status")
async def status():
    return get_status()

@app.get("/signals")
async def signals():
    return get_signals_dict()

@app.get("/prices")
async def prices(
    instrument_id: str = Query(..., description="ID del instrumento definido en instruments.yaml"),
    points: int = Query(60, ge=10, le=400),
    provider: str = Query("auto", pattern="^(auto|tiingo|yfinance)$"),
):
    # 1) Buscar el instrumento por ID
    insts = load_instruments()
    match = next((i for i in insts if i.instrument_id == instrument_id), None)
    if not match:
        raise HTTPException(status_code=404, detail="instrument_id not found")

    # 2) Traer barras según proveedor
    bars = []
    # Happy path: Tiingo si el instrumento lo declara o si se fuerza por query
    if provider in ("auto", "tiingo") and (match.source == "tiingo" or provider == "tiingo"):
        bars = await tiingo_fetch_daily(match, days=180)

    # (Opcional) Fallback a yfinance solo si lo pedís explícitamente
    if not bars and provider == "yfinance":
        yf = YFPrices()
        try:
            bars_all = await yf.fetch_bars([match], timeframe="1d")
        except TypeError:
            bars_all = yf._fetch_many(match)  # si tu fetch_bars fuera sync
        bars = [b for b in bars_all if getattr(b, "instrument_id", None) == instrument_id]

    # 3) Serie de salida
    series = [{"t": b.ts.isoformat(), "c": b.close} for b in bars[-points:]] if bars else []
    return {
        "instrument_id": instrument_id,
        "series": series,
        "provider": (bars[0].provider if bars else provider),
    }

@app.post("/run-tick")
async def run_tick(background: BackgroundTasks, authorization: str | None = Header(None)):
    if AGENT_TOKEN and authorization != f"Bearer {AGENT_TOKEN}":
        raise HTTPException(status_code=401, detail="Unauthorized")
    async def _run():
        rules = await load_rules()
        await agent_tick(rules)
    background.add_task(_run)
    return {"ok": True}

@app.post("/run-tick-sync")
async def run_tick_sync(authorization: str | None = Header(None)):
    if AGENT_TOKEN and authorization != f"Bearer {AGENT_TOKEN}":
        raise HTTPException(status_code=401, detail="Unauthorized")
    rules = await load_rules()
    await agent_tick(rules)
    return {"ok": True}


import os, yaml
from fastapi import FastAPI, HTTPException, BackgroundTasks, Header
from pydantic import BaseModel
from pathlib import Path
from normalize.instruments import load_instruments, save_instruments
from fastapi.middleware.cors import CORSMiddleware
from agent.main import load_rules, tick as agent_tick



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

@app.post("/run-tick")
async def run_tick(background: BackgroundTasks):
    async def _run():
        rules = await load_rules()
        await agent_tick(rules)
    background.add_task(_run)
    return {"ok": True}

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
    return {"ok": True}

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

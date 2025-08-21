import os, yaml
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pathlib import Path
from normalize.instruments import load_instruments, save_instruments

app = FastAPI(title="Market Agent API")

class NewInstrument(BaseModel):
    symbol: str
    instrument_id: str
    type: str
    currency: str = "ARS"
    source: str = "yfinance"

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

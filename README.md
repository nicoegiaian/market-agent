# Market Agent (MVP)

Agente modular para ingestar precios (yfinance), evaluar reglas y enviar alertas (consola/Telegram). Incluye API FastAPI para alta de instrumentos y lectura de reglas.

## Requisitos
- Python 3.11+
- (Opcional) cuenta de Telegram Bot para notificaciones

## Setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # y completa si usarás Telegram
```

## Correr
Terminal 1 (web):
```bash
uvicorn api.app:app --reload
```
Terminal 2 (worker):
```bash
python -m agent.main
```

## Agregar instrumentos
- Editá `config/instruments.yaml` **o** usá el endpoint:
```bash
curl -X POST http://127.0.0.1:8000/instruments \
  -H 'Content-Type: application/json' \
  -d '{"symbol":"PAMP.BA","instrument_id":"ISIN-AR-PAMP","type":"equity","currency":"ARS","source":"yfinance"}'
```

## Reglas
- Declaradas en `config/rules.yaml`. El worker las carga al arrancar.
- Ejemplo incluido: `momentum_breakout`.

## Deploy en Render
- Subí este repo a GitHub.
- En Render: **New +** → **Blueprint** → conectá el repo → elegí `render.yaml`.
- Se crean dos servicios: "market-agent-web" y "market-agent-worker".

## Próximos pasos
- Persistencia real en Supabase/TimescaleDB.
- Conectores adicionales (IOL, pyRofex, BYMA).
- News + embeddings y reglas basadas en eventos.
- UI (React) para Dashboard/Rules/Signals.

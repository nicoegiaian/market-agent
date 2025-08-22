import asyncio, os, yaml
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict
from normalize.instruments import load_instruments
from connectors.prices.yfinance import YFPrices
from rules_engine.registry import RULES_REGISTRY
from models import Signal
from agent.state import set_last_tick, set_signals

SETTINGS = yaml.safe_load(Path("config/settings.yaml").read_text())
RULES_CFG = yaml.safe_load(Path("config/rules.yaml").read_text())

async def load_rules():
    # importar side-effect para registrar reglas
    from rules_engine.rules import momentum_breakout  # noqa
    active = {}
    for r in RULES_CFG:
        if r.get("enabled"):
            cls = RULES_REGISTRY[r["id"]]
            active[r["id"]] = cls(r.get("params", {}))
    return active

async def gather_bars():
    instruments = load_instruments()
    yf = YFPrices()
    bars = await yf.fetch_bars(instruments, timeframe="1d")
    # historial corto por demo: un solo bar actual por instrumento
    by_inst = defaultdict(list)
    for b in bars:
        by_inst[b.instrument_id].append(b)
    return by_inst

async def notify(signals: list[Signal]):
    channel = SETTINGS.get("notify", {}).get("channel", "console")
    if channel == "telegram":
        from notify.telegram import TelegramNotifier
        n = TelegramNotifier()
    else:
        from notify.console import ConsoleNotifier
        n = ConsoleNotifier()
    await n.send(signals)

async def tick(rules):
    bars_by_inst = await gather_bars()
    all_signals = []
    for rid, rule in rules.items():
        sigs = await rule.compute(bars_by_inst)
        all_signals.extend(sigs)
    # NUEVO: guardar estado en memoria para la API
    set_signals(all_signals)
    set_last_tick(datetime.utcnow())
    if all_signals:
        await notify(all_signals)


async def main():
    rules = await load_rules()
    interval = SETTINGS["app"].get("rules_tick_sec", 15)
    while True:
        try:
            await tick(rules)
        except Exception as e:
            print("[agent] error:", e)
        await asyncio.sleep(interval)

if __name__ == "__main__":
    asyncio.run(main())


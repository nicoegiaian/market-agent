import yaml
from models import Instrument
from pathlib import Path

CFG_PATH = Path("config/instruments.yaml")

def load_instruments() -> list[Instrument]:
    data = yaml.safe_load(CFG_PATH.read_text())
    return [Instrument(**row) for row in data]

def save_instruments(items: list[Instrument]):
    data = [i.model_dump() for i in items]
    CFG_PATH.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True))

from pydantic import BaseModel

class Instrument(BaseModel):
    symbol: str
    instrument_id: str
    type: str  # equity | bond
    currency: str
    source: str

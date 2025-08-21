from abc import ABC, abstractmethod
from typing import Iterable, List
from models import Bar, Instrument

class PricesConnector(ABC):
    @abstractmethod
    async def fetch_bars(self, instruments: Iterable[Instrument], timeframe: str = "1d") -> List[Bar]:
        ...

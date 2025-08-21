from abc import ABC, abstractmethod
from typing import Iterable
from models import Signal

class Notifier(ABC):
    @abstractmethod
    async def send(self, signals: Iterable[Signal]):
        ...

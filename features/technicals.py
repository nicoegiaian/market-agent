from collections import deque
from typing import Dict, Deque

class Rolling:
    def __init__(self, window: int):
        self.window = window
        self.buf: Deque[float] = deque(maxlen=window)
    def add(self, x: float) -> None:
        self.buf.append(x)
    def sma(self) -> float:
        return sum(self.buf)/len(self.buf) if self.buf else 0.0

class ZScore:
    def __init__(self, window: int):
        self.window = window
        self.buf: Deque[float] = deque(maxlen=window)
    def add(self, x: float):
        self.buf.append(x)
    def z(self) -> float:
        n = len(self.buf)
        if n < 2:
            return 0.0
        mean = sum(self.buf)/n
        var = sum((v-mean)**2 for v in self.buf)/ (n-1)
        std = var ** 0.5
        return 0.0 if std==0 else (self.buf[-1]-mean)/std

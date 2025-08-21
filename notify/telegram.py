import os, asyncio
from typing import Iterable
from models import Signal
import httpx

BOT=os.getenv("TELEGRAM_BOT_TOKEN")
CHAT=os.getenv("TELEGRAM_CHAT_ID")

class TelegramNotifier:
    async def send(self, signals: Iterable[Signal]):
        if not BOT or not CHAT:
            return
        async with httpx.AsyncClient(timeout=10) as client:
            for s in signals:
                msg=f"\u26A0\uFE0F {s.instrument_id} {s.direction.upper()} (score {s.score:.2f})\n{ s.reason }"
                url=f"https://api.telegram.org/bot{BOT}/sendMessage"
                await client.post(url, json={"chat_id": CHAT, "text": msg})

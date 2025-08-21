from datetime import datetime
from models import Signal
from rules_engine.registry import register

@register("momentum_breakout")
class MomentumBreakout:
    def __init__(self, params: dict):
        self.sma_window = int(params.get("sma_window", 20))
        self.min_z = float(params.get("min_zscore", 1.0))
    async def compute(self, bars_by_inst: dict[str, list]):
        signals: list[Signal] = []
        for inst_id, bars in bars_by_inst.items():
            if not bars:
                continue
            closes = [b.close for b in bars[-self.sma_window:]]
            if not closes:
                continue
            sma = sum(closes)/len(closes)
            last = bars[-1].close
            z = 0.0
            if len(closes) > 1:
                m = sum(closes)/len(closes)
                var = sum((x-m)**2 for x in closes)/(len(closes)-1)
                std = var**0.5
                z = 0.0 if std==0 else (last-m)/std
            if z >= self.min_z and last > sma:
                signals.append(Signal(
                    instrument_id=inst_id,
                    rule_id="momentum_breakout",
                    ts=datetime.utcnow(),
                    direction="buy",
                    score=min(1.0, z/3.0),
                    reason=f"Last>{self.sma_window}SMA y z={z:.2f}",
                    details={"last": last, "sma": sma, "z": z},
                ))
        return signals

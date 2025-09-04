import { useEffect, useState } from "react";
import { fetchPrices } from "@/lib/api";
import SparklinePercent from "./SparklinePercent";

const TF = [
  { label: "1D", range: "1d", interval: "5min" },
  { label: "5D", range: "5d", interval: "15min" },
  { label: "1M", range: "1mo", interval: "1hour" },
  { label: "3M", range: "3mo", interval: "4hour" },
  { label: "1Y", range: "1y", interval: "1day" },
];

export function InstrumentCard({ symbol, name }: { symbol: string; name: string }) {
  const [tf, setTf] = useState(TF[1]); // 5D default
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<Awaited<ReturnType<typeof fetchPrices>> | null>(null);

  useEffect(() => {
    let alive = true;
    setLoading(true);
    fetchPrices(symbol, tf.range, tf.interval)
      .then((d) => { if (alive) setData(d); })
      .finally(() => alive && setLoading(false));
    return () => { alive = false; };
  }, [symbol, tf]);

  const series = (data?.series ?? []).map(p => ({ t: p.t, c: p.c }));
  const last = data?.quote?.last ?? series.at(-1)?.c ?? null;
  const base = series[0]?.c ?? null;
  const pct = (last && base) ? ((last - base) / base) * 100 : 0;
  const isUp = (pct ?? 0) >= 0;

  return (
    <div className="rounded-2xl border p-3 shadow-sm">
      <div className="flex items-baseline justify-between">
        <div>
          <div className="text-sm text-gray-500">{name}</div>
          <div className="text-lg font-semibold">{symbol}</div>
        </div>
        <div className="text-right">
          <div className="text-xl font-bold">{last ? last.toFixed(2) : "-"}</div>
          <div className={isUp ? "text-green-600" : "text-red-600"}>
            {pct ? `${pct.toFixed(2)}%` : "--"}
          </div>
        </div>
      </div>

      <div className="mt-2">
        {loading ? <div className="text-sm text-gray-400">Cargando…</div> : <SparklinePercent series={series} />}
      </div>

      <div className="mt-2 flex gap-2">
        {TF.map(opt => (
          <button
            key={opt.label}
            onClick={() => setTf(opt)}
            className={`px-2 py-1 rounded-full text-xs border ${tf.label === opt.label ? "bg-black text-white" : "bg-white"}`}
          >
            {opt.label}
          </button>
        ))}
      </div>
    </div>
  );
}


import { useMemo } from "react";
import { LineChart, Line, XAxis, YAxis, ResponsiveContainer, Tooltip, ReferenceDot } from "recharts";

type Pt = { t: string; c: number; pct: number };

export default function SparklinePercent({ series }: { series: { t:string; c:number }[] }) {
  const data: Pt[] = useMemo(() => {
    if (!series?.length) return [];
    const base = series[0].c;
    return series.map(p => ({
      t: p.t,
      c: p.c,
      pct: base ? (p.c - base) / base * 100 : 0
    }));
  }, [series]);

  const last = data.at(-1)?.pct ?? 0;
  const isUp = last >= 0;

  return (
    <div className="h-24">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ left: 0, right: 0, top: 8, bottom: 0 }}>
          <XAxis dataKey="t" hide />
          <YAxis hide domain={["auto","auto"]} />
          <Tooltip
            formatter={(value: any, name: any) =>
              name === "pct" ? [`${(value as number).toFixed(2)}%`, "Δ"] : [value, name]
            }
            labelFormatter={(l) => new Date(l as string).toLocaleString()}
          />
          <Line
            type="monotone"
            dataKey="pct"
            stroke={isUp ? "green" : "red"}
            dot={false}
            strokeWidth={2}
          />
          <ReferenceDot x={data[0]?.t} y={0} isFront r={0} /> {/* baseline */}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}


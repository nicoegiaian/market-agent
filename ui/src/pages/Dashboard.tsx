import { useEffect, useState } from "react";
import { fetchInstruments } from "@/lib/api";
import { InstrumentCard } from "@/components/InstrumentCard";

export default function Dashboard() {
  const [instruments, setInstruments] = useState<{ symbol: string; name: string }[]>([]);
  const [err, setErr] = useState("");

  useEffect(() => {
    fetchInstruments().then(setInstruments).catch(e => setErr(String(e)));
  }, []);

  return (
    <div>
      {err && <div className="text-red-700 text-sm mb-2">{err}</div>}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {instruments.map(inst => (
          <InstrumentCard key={inst.symbol} symbol={inst.symbol} name={inst.name} />
        ))}
      </div>
    </div>
  );
}


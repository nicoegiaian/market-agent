// lib/api.ts
const BASE = import.meta.env.VITE_API_BASE ?? "http://localhost:8000";

if (!import.meta.env.VITE_API_BASE) {
  console.warn(
    "VITE_API_BASE no está definido; usando http://localhost:8000 como valor por defecto"
  );
}

export async function fetchInstruments() {
  const r = await fetch(`${BASE}/instruments`);
  if (!r.ok) throw new Error("Failed instruments");
  const data = await r.json();
  if (!Array.isArray(data) && !Array.isArray(data.items)) {
    console.warn("fetchInstruments: unexpected response", data);
  }
  return Array.isArray(data) ? data : data.items ?? [];
}

export async function fetchPrices(symbol: string, range = "5d", interval = "5min") {
  const url = new URL(`${BASE}/prices`);
  url.searchParams.set("symbol", symbol);
  url.searchParams.set("range", range);
  url.searchParams.set("interval", interval);
  const r = await fetch(url);
  if (!r.ok) throw new Error("Failed prices");
  return await r.json() as {
    symbol:string,
    quote: { last:number|null; prevClose:number|null; ts:string|null },
    series: { t:string; o:number; h:number; l:number; c:number; v:number }[]
  };
}

// ---- Stubs para mantener el build estable mientras migrás ----
export type Rule = { id: string; kind: string; enabled: boolean };

// Si ya tenés endpoints reales, reemplazá por fetch a tu backend.
export async function getRules(): Promise<Rule[]> {
  return []; // TODO: reemplazar por fetch(`${BASE}/rules`)
}

export async function getSignals(): Promise<any[]> {
  return []; // TODO: reemplazar por fetch(`${BASE}/signals`)
}

export async function addInstrument(body: {
  symbol: string;
  instrument_id: string;
  type: string;
  currency: string;
  source: string;
}): Promise<{ ok: boolean }> {
  // TODO: reemplazar por POST `${BASE}/instruments`
  return { ok: true };
}


// lib/api.ts
const BASE = import.meta.env.VITE_API_BASE; // Render API

export async function fetchInstruments() {
  const r = await fetch(`${BASE}/instruments`);
  if (!r.ok) throw new Error("Failed instruments");
  return (await r.json()).items as {symbol:string; name:string}[];
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


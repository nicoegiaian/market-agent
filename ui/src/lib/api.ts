const BASE = import.meta.env.VITE_API_URL?.replace(/\/$/, '') || ''

export async function api<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...(init?.headers||{}) },
    ...init,
  })
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`)
  return res.json() as Promise<T>
}

export type Rule = {
  id: string; kind: string; enabled: boolean; params: Record<string, unknown>; notify?: { channel: string; min_score?: number }
}

export async function getHealth() { return api<{status:string}>('/healthz') }
export async function getRules() { return api<Rule[]>('/rules') }
export async function addInstrument(body: {
  symbol: string; instrument_id: string; type: string; currency?: string; source?: string;
}) { return api<{ok: boolean}>('/instruments', { method: 'POST', body: JSON.stringify(body) }) }

export type Instrument = { symbol: string; instrument_id: string; type: string; currency: string; source: string }

export async function getStatus() { return api<{last_tick: string|null; signals_count: number}>('/status') }
export async function getInstruments() { return api<Instrument[]>('/instruments') }
export async function getPrices(instrument_id: string) {
  return api<{instrument_id: string; series: {t:string; c:number}[]}>('/prices?instrument_id='+encodeURIComponent(instrument_id))
}
export async function getSignals() {
  return api<Array<{instrument_id:string; rule_id:string; ts:string; direction:'buy'|'sell'|'watch'; score:number; reason:string; details:any}>>('/signals')
}


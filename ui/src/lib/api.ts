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

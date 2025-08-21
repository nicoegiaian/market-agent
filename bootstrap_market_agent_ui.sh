#!/usr/bin/env bash
# Bootstrap UI (React + Vite + Tailwind + React Router + Recharts)
# Crea la carpeta ./ui con un frontend MVP que consume tu API FastAPI.
# Uso:
#   bash bootstrap_market_agent_ui.sh
#   cd ui && npm install && npm run dev
# Para deploy en Vercel: setear VITE_API_URL como env var.

set -euo pipefail
ROOT_DIR=$(pwd)
UI_DIR="ui"
mkdir -p "$UI_DIR"
cd "$UI_DIR"

# --- package.json ---
cat > package.json <<'EOF'
{
  "name": "market-agent-ui",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc -b && vite build",
    "preview": "vite preview --port 5173"
  },
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "react-router-dom": "^6.26.2",
    "recharts": "^2.12.7",
    "lucide-react": "^0.469.0",
    "clsx": "^2.1.1"
  },
  "devDependencies": {
    "@types/react": "^18.3.3",
    "@types/react-dom": "^18.3.0",
    "autoprefixer": "^10.4.20",
    "postcss": "^8.4.47",
    "tailwindcss": "^3.4.10",
    "typescript": "^5.5.4",
    "vite": "^5.4.2"
  }
}
EOF

# --- tsconfig ---
cat > tsconfig.json <<'EOF'
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "Bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"]
    }
  },
  "include": ["src"]
}
EOF

cat > tsconfig.node.json <<'EOF'
{
  "compilerOptions": {
    "composite": true,
    "skipLibCheck": true,
    "module": "ESNext",
    "moduleResolution": "Bundler",
    "allowSyntheticDefaultImports": true
  },
  "include": ["vite.config.ts"]
}
EOF

# --- vite ---
cat > vite.config.ts <<'EOF'
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: { port: 5173 }
})
EOF

# --- tailwind ---
cat > tailwind.config.ts <<'EOF'
import type { Config } from 'tailwindcss'

export default {
  content: [
    './index.html',
    './src/**/*.{ts,tsx}',
  ],
  theme: {
    extend: {},
  },
  plugins: [],
} satisfies Config
EOF

cat > postcss.config.js <<'EOF'
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
EOF

# --- index.html ---
cat > index.html <<'EOF'
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Market Agent</title>
  </head>
  <body class="bg-slate-50">
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
EOF

# --- src ---
mkdir -p src/pages src/components src/lib

cat > src/index.css <<'EOF'
@tailwind base;
@tailwind components;
@tailwind utilities;

:root { color-scheme: light dark; }
body { @apply text-slate-800; }
.card { @apply bg-white rounded-2xl shadow p-5; }
.btn { @apply inline-flex items-center justify-center rounded-xl px-4 py-2 border border-slate-300 hover:bg-slate-50; }
.input { @apply w-full rounded-xl border border-slate-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-slate-300; }
.label { @apply text-sm text-slate-600 mb-1; }
EOF

cat > src/main.tsx <<'EOF'
import React from 'react'
import ReactDOM from 'react-dom/client'
import { createBrowserRouter, RouterProvider } from 'react-router-dom'
import App from './App'
import './index.css'
import Dashboard from './pages/Dashboard'
import Instruments from './pages/Instruments'
import Rules from './pages/Rules'

const router = createBrowserRouter([
  {
    path: '/',
    element: <App />,
    children: [
      { index: true, element: <Dashboard /> },
      { path: 'instruments', element: <Instruments /> },
      { path: 'rules', element: <Rules /> },
    ],
  },
])

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>
)
EOF

cat > src/App.tsx <<'EOF'
import { Link, NavLink, Outlet } from 'react-router-dom'
import { Activity, Settings2, Gauge } from 'lucide-react'

export default function App() {
  return (
    <div className="min-h-dvh">
      <header className="sticky top-0 z-10 bg-white border-b border-slate-200">
        <div className="max-w-6xl mx-auto px-4 py-3 flex items-center gap-4">
          <Link to="/" className="flex items-center gap-2 font-semibold">
            <Activity className="w-5 h-5"/>
            Market Agent
          </Link>
          <nav className="ml-auto flex items-center gap-2">
            <NavLink to="/" end className={({isActive})=>`btn ${isActive? 'bg-slate-100' : ''}` }>
              <Gauge className="w-4 h-4 mr-2"/> Dashboard
            </NavLink>
            <NavLink to="/instruments" className={({isActive})=>`btn ${isActive? 'bg-slate-100' : ''}` }>
              + Instruments
            </NavLink>
            <NavLink to="/rules" className={({isActive})=>`btn ${isActive? 'bg-slate-100' : ''}` }>
              <Settings2 className="w-4 h-4 mr-2"/> Rules
            </NavLink>
          </nav>
        </div>
      </header>
      <main className="max-w-6xl mx-auto px-4 py-6">
        <Outlet />
      </main>
    </div>
  )
}
EOF

# --- lib/api ---
cat > src/lib/api.ts <<'EOF'
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
EOF

# --- pages/Dashboard ---
cat > src/pages/Dashboard.tsx <<'EOF'
import { useEffect, useMemo, useState } from 'react'
import { getHealth, getRules, type Rule } from '@/lib/api'
import { LineChart, Line, XAxis, YAxis, ResponsiveContainer, Tooltip } from 'recharts'

// Nota: este gráfico usa datos mock hasta que exista GET /prices
function Sparkline() {
  const data = useMemo(() => Array.from({length: 24}, (_,i)=>({x:i, y: 100 + Math.sin(i/2)*5 + Math.random()*2})), [])
  return (
    <div className="h-24">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{left: 0, right: 0, top: 8, bottom: 0}}>
          <Line type="monotone" dataKey="y" dot={false} strokeWidth={2} />
          <XAxis dataKey="x" hide /><YAxis hide />
          <Tooltip />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}

export default function Dashboard() {
  const [health, setHealth] = useState<string>('…')
  const [rules, setRules] = useState<Rule[]>([])
  const [err, setErr] = useState<string>('')

  useEffect(()=>{
    getHealth().then(r=>setHealth(r.status)).catch(e=>setErr(String(e)))
    getRules().then(setRules).catch(()=>{})
  },[])

  return (
    <div className="space-y-6">
      <div className="grid md:grid-cols-3 gap-4">
        <div className="card">
          <div className="text-sm text-slate-600">API Health</div>
          <div className="text-xl font-semibold mt-1">{health}</div>
          {err && <div className="text-xs text-red-600 mt-2">{err}</div>}
        </div>
        <div className="card">
          <div className="text-sm text-slate-600">Active Rules</div>
          <div className="text-xl font-semibold mt-1">{rules.filter(r=>r.enabled).length}</div>
        </div>
        <div className="card">
          <div className="text-sm text-slate-600">Preview Sparkline</div>
          <Sparkline />
        </div>
      </div>

      <div className="card">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-lg font-semibold">Rules</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full text-sm">
            <thead>
              <tr className="text-left text-slate-600">
                <th className="py-2 pr-4">ID</th>
                <th className="py-2 pr-4">Kind</th>
                <th className="py-2 pr-4">Enabled</th>
                <th className="py-2 pr-4">Params</th>
              </tr>
            </thead>
            <tbody>
              {rules.map(r=> (
                <tr key={r.id} className="border-t">
                  <td className="py-2 pr-4 font-mono">{r.id}</td>
                  <td className="py-2 pr-4">{r.kind}</td>
                  <td className="py-2 pr-4">{r.enabled? 'Yes':'No'}</td>
                  <td className="py-2 pr-4 text-slate-600">
                    <pre className="whitespace-pre-wrap">{JSON.stringify(r.params, null, 2)}</pre>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
EOF

# --- pages/Instruments ---
cat > src/pages/Instruments.tsx <<'EOF'
import { useState } from 'react'
import { addInstrument } from '@/lib/api'

export default function Instruments(){
  const [form, setForm] = useState({ symbol: '', instrument_id: '', type: 'equity', currency: 'ARS', source: 'yfinance' })
  const [msg, setMsg] = useState('')
  const [err, setErr] = useState('')

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setMsg(''); setErr('')
    try {
      await addInstrument(form)
      setMsg('Instrument added successfully.')
    } catch (e:any) {
      setErr(e?.message || 'Error adding instrument')
    }
  }

  return (
    <div className="max-w-xl">
      <div className="card">
        <h2 className="text-lg font-semibold mb-4">Add Instrument</h2>
        <form onSubmit={onSubmit} className="space-y-3">
          <div>
            <div className="label">Symbol</div>
            <input className="input" value={form.symbol} onChange={e=>setForm({...form, symbol: e.target.value})} placeholder="GGAL.BA" required />
          </div>
          <div>
            <div className="label">Instrument ID</div>
            <input className="input" value={form.instrument_id} onChange={e=>setForm({...form, instrument_id: e.target.value})} placeholder="ISIN-AR-GGAL" required />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <div className="label">Type</div>
              <select className="input" value={form.type} onChange={e=>setForm({...form, type: e.target.value})}>
                <option value="equity">equity</option>
                <option value="bond">bond</option>
              </select>
            </div>
            <div>
              <div className="label">Currency</div>
              <input className="input" value={form.currency} onChange={e=>setForm({...form, currency: e.target.value})} />
            </div>
          </div>
          <div>
            <div className="label">Source</div>
            <input className="input" value={form.source} onChange={e=>setForm({...form, source: e.target.value})} />
          </div>
          <div className="flex items-center gap-2 pt-2">
            <button className="btn" type="submit">Save</button>
            {msg && <span className="text-green-700 text-sm">{msg}</span>}
            {err && <span className="text-red-700 text-sm">{err}</span>}
          </div>
        </form>
      </div>
    </div>
  )
}
EOF

# --- pages/Rules ---
cat > src/pages/Rules.tsx <<'EOF'
import { useEffect, useState } from 'react'
import { getRules, type Rule } from '@/lib/api'

export default function Rules(){
  const [rules, setRules] = useState<Rule[]>([])
  const [err, setErr] = useState('')

  useEffect(()=>{ getRules().then(setRules).catch(e=>setErr(String(e))) },[])

  return (
    <div className="card">
      <h2 className="text-lg font-semibold mb-4">Rules</h2>
      {err && <div className="text-red-700 text-sm mb-2">{err}</div>}
      <div className="space-y-2">
        {rules.map(r=> (
          <div key={r.id} className="border rounded-xl p-3">
            <div className="font-mono text-sm">{r.id}</div>
            <div className="text-slate-600 text-sm">{r.kind} • {r.enabled? 'enabled':'disabled'}</div>
          </div>
        ))}
      </div>
    </div>
  )
}
EOF

# --- env types (vite) ---
cat > src/vite-env.d.ts <<'EOF'
/// <reference types="vite/client" />
EOF

# --- README ---
cat > README.md <<'EOF'
# Market Agent UI (MVP)

- React + Vite + Tailwind + Router + Recharts
- Requiere variable de entorno `VITE_API_URL` apuntando a tu API FastAPI

## Scripts
- `npm run dev` — local dev (http://localhost:5173)
- `npm run build` — build para producción
- `npm run preview` — sirve el build localmente

## Entorno
En Vercel, seteá en **Project Settings → Environment Variables**:
- `VITE_API_URL = https://<tu-servicio-en-render>.onrender.com`

## API esperada
- `GET /healthz` → `{ status: "ok" }`
- `GET /rules` → `Rule[]`
- `POST /instruments` → `{ ok: true }` con body `{ symbol, instrument_id, type, currency, source }`

## Notas
- El sparkline usa datos mock hasta que exista `GET /prices`.
- Para CORS en la API, habilitá tu dominio de Vercel.
EOF

printf "\nUI creada en %s. Ejecutá:\n  cd ui\n  npm install\n  npm run dev\n" "$ROOT_DIR/$UI_DIR"

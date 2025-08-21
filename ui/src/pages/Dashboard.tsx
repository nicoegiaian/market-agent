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

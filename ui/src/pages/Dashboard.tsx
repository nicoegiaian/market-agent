import { useEffect, useState } from 'react'
import { getHealth, getRules, getStatus, getInstruments, getPrices, type Rule } from '@/lib/api'
import { LineChart, Line, XAxis, YAxis, ResponsiveContainer, Tooltip } from 'recharts'

function Sparkline({ data }: { data: {x:number; y:number}[] }) {
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
  const [health, setHealth] = useState('…')
  const [rules, setRules] = useState<Rule[]>([])
  const [status, setStatus] = useState<{last_tick:string|null; signals_count:number}>({last_tick:null, signals_count:0})
  const [symbols, setSymbols] = useState<{label:string; id:string}[]>([])
  const [selected, setSelected] = useState<string>('')
  const [series, setSeries] = useState<{x:number; y:number}[]>([])
  const [err, setErr] = useState('')

  useEffect(()=>{
    getHealth().then(r=>setHealth(r.status)).catch(e=>setErr(String(e)))
    getRules().then(setRules).catch(()=>{})
    getStatus().then(setStatus).catch(()=>{})
    getInstruments().then(list=>{
      const opts = list.map(i=>({label: i.symbol, id: i.instrument_id}))
      setSymbols(opts)
      if (opts[0]) setSelected(opts[0].id)
    }).catch(()=>{})
  },[])

  useEffect(()=>{
    if (!selected) return
    getPrices(selected).then(r=>{
      const data = r.series.map((p, idx)=>({x: idx, y: p.c}))
      setSeries(data)
    }).catch(()=>setSeries([]))
  },[selected])

  return (
    <div className="space-y-6">
      <div className="grid md:grid-cols-4 gap-4">
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
          <div className="text-sm text-slate-600">Last Tick (UTC)</div>
          <div className="text-xl font-semibold mt-1">{status.last_tick ? new Date(status.last_tick).toLocaleString() : '—'}</div>
          <div className="text-xs text-slate-500 mt-1">Signals last tick: {status.signals_count}</div>
        </div>
        <div className="card">
          <div className="text-sm text-slate-600 mb-2">Instrument</div>
          <select className="input" value={selected} onChange={e=>setSelected(e.target.value)}>
            {symbols.map(o=> <option value={o.id} key={o.id}>{o.label}</option>)}
          </select>
        </div>
      </div>

      <div className="card">
        <div className="text-sm text-slate-600 mb-2">Price (sparkline)</div>
        <Sparkline data={series} />
      </div>

      <div className="card">
        <h2 className="text-lg font-semibold mb-3">Rules</h2>
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


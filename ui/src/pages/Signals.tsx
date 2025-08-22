import { useEffect, useState } from 'react'
import { getSignals } from '@/lib/api'

export default function Signals(){
  const [rows, setRows] = useState<Awaited<ReturnType<typeof getSignals>>>([])

  useEffect(()=>{ getSignals().then(setRows).catch(()=>setRows([])) },[])

  return (
    <div className="space-y-3">
      <h2 className="text-lg font-semibold">Signals (last tick)</h2>
      {rows.length===0 && <div className="text-slate-500 text-sm">No signals yet.</div>}
      <div className="grid md:grid-cols-2 gap-3">
        {rows.map((s, i)=> (
          <div key={i} className="card">
            <div className="flex items-center justify-between">
              <div className="font-mono text-sm">{s.instrument_id}</div>
              <div className={`text-xs px-2 py-1 rounded ${s.direction==='buy'?'bg-green-100 text-green-700': s.direction==='sell'?'bg-red-100 text-red-700':'bg-slate-100 text-slate-700'}`}>
                {s.direction.toUpperCase()}
              </div>
            </div>
            <div className="text-slate-600 text-sm mt-1">{s.rule_id} • score {s.score.toFixed(2)}</div>
            <div className="text-slate-700 text-sm mt-2">{s.reason}</div>
          </div>
        ))}
      </div>
    </div>
  )
}


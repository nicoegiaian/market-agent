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

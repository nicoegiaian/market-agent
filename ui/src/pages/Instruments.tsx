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

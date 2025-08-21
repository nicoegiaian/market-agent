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

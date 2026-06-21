import { ReactNode } from 'react'
import { ScanSearch, Camera, List, BarChart3, Sparkles } from 'lucide-react'

const TABS = [
  { id: 'erfassen', label: 'Erfassen', icon: Camera },
  { id: 'historie', label: 'Historie', icon: List },
  { id: 'analyse', label: 'Analyse', icon: BarChart3 },
]

export default function Layout({
  active, setTab, provider, children,
}: { active: string; setTab: (t: string) => void; provider: string; children: ReactNode }) {
  const live = provider.startsWith('anthropic')
  return (
    <div className="min-h-screen flex flex-col md:flex-row">
      <aside
        className="md:w-60 p-4 md:p-5 md:min-h-screen border-b md:border-b-0 md:border-r"
        style={{ borderColor: 'var(--glass-border)' }}
      >
        <div className="flex items-center gap-2 mb-6 md:mb-8">
          <div className="glass glow-cyan p-2 rounded-xl"><ScanSearch size={22} color="#22d3ee" /></div>
          <div>
            <div className="font-bold text-lg leading-none text-grad">AusschussLens</div>
            <div className="text-[11px] mt-1" style={{ color: 'var(--muted)' }}>8D in 30 Sekunden</div>
          </div>
        </div>
        <nav className="flex md:flex-col gap-2">
          {TABS.map((t) => {
            const Icon = t.icon
            const on = active === t.id
            return (
              <button
                key={t.id}
                onClick={() => setTab(t.id)}
                className="btn justify-start flex-1 md:flex-none"
                style={on ? { background: 'linear-gradient(90deg,rgba(34,211,238,.18),rgba(168,85,247,.18))', borderColor: 'rgba(34,211,238,.5)' } : {}}
              >
                <Icon size={18} /> {t.label}
              </button>
            )
          })}
        </nav>
        <div className="badge glass mt-6 md:mt-8" style={{ padding: '6px 10px' }}>
          <Sparkles size={13} color={live ? '#a855f7' : '#8b97ad'} /> {live ? 'Claude live' : 'Mock-Modus'}
        </div>
      </aside>
      <main className="flex-1 p-4 md:p-8 w-full" style={{ maxWidth: 1200, marginLeft: 'auto', marginRight: 'auto' }}>
        {children}
      </main>
    </div>
  )
}

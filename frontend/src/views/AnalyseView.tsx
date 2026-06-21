import { useEffect, useState } from 'react'
import GlowCard from '../components/GlowCard'
import StatCard from '../components/StatCard'
import { api, Analytics, catHex, euro } from '../api'
import { BarChart, Bar, XAxis, YAxis, ResponsiveContainer, Cell, Tooltip } from 'recharts'
import { Euro, AlertTriangle, Layers, Boxes } from 'lucide-react'

const tooltipStyle = { background: '#0f172a', border: '1px solid rgba(255,255,255,.1)', borderRadius: 12, color: '#e7ecf5' }

export default function AnalyseView({ version }: { version: number }) {
  const [a, setA] = useState<Analytics | null>(null)
  useEffect(() => { api.analytics().then(setA).catch(() => {}) }, [version])
  if (!a) return <div style={{ color: 'var(--muted)' }}>Lade Analyse…</div>

  const causeData = a.by_cause.slice(0, 8).map((c) => ({ name: c.name, cost: c.cost, category: c.category }))
  const machData = a.by_machine.map((m) => ({ name: m.code, cost: m.cost }))

  return (
    <div>
      <h1 className="text-2xl font-bold mb-1">Kosten-Analyse</h1>
      <p className="mb-6" style={{ color: 'var(--muted)' }}>Wo das Ausschuss-Geld wirklich verbrennt.</p>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-5">
        <StatCard label="Ausschuss gesamt" value={euro(a.total_cost, 0)} icon={<Euro size={16} color="#22d3ee" />} />
        <StatCard label="Vorfälle" value={a.event_count} sub={`${a.open_count} offen`} icon={<Layers size={16} color="#a855f7" />} />
        <StatCard label="Ausschuss-Teile" value={a.total_qty} icon={<Boxes size={16} color="#38bdf8" />} />
        <StatCard label="Top-Ursache" value={`${a.top_cause_share}%`} sub={a.top_cause?.name} icon={<AlertTriangle size={16} color="#f59e0b" />} />
      </div>

      {a.top_cause && a.top_machine && (
        <GlowCard glow="cyan" className="p-4 mb-5">
          <div className="text-sm md:text-base">
            <AlertTriangle size={16} color="#f59e0b" className="inline mr-2" />
            <b style={{ color: '#fcd34d' }}>{a.top_cause.name}</b> verursacht <b className="text-grad">{a.top_cause_share}%</b> der Ausschusskosten —
            Schwerpunkt <b>{a.top_machine.name}</b> ({a.top_machine_share}%, {euro(a.top_machine.cost, 0)}).
          </div>
        </GlowCard>
      )}

      <div className="grid md:grid-cols-2 gap-5">
        <GlowCard className="p-5">
          <h2 className="font-semibold mb-4">Pareto · Kosten nach Ursache</h2>
          <ResponsiveContainer width="100%" height={320}>
            <BarChart data={causeData} layout="vertical" margin={{ left: 10, right: 20 }}>
              <XAxis type="number" tick={{ fill: '#8b97ad', fontSize: 11 }} tickFormatter={(v) => `${Math.round(Number(v))}€`} />
              <YAxis type="category" dataKey="name" width={150} tick={{ fill: '#cbd5e1', fontSize: 11 }} />
              <Tooltip cursor={{ fill: 'rgba(255,255,255,.04)' }} contentStyle={tooltipStyle} formatter={(v: any) => [euro(Number(v)), 'Kosten']} />
              <Bar dataKey="cost" radius={[0, 6, 6, 0]}>
                {causeData.map((c, i) => <Cell key={i} fill={catHex(c.category)} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </GlowCard>

        <GlowCard className="p-5">
          <h2 className="font-semibold mb-4">Kosten nach Maschine</h2>
          <ResponsiveContainer width="100%" height={320}>
            <BarChart data={machData} margin={{ left: 0, right: 10 }}>
              <XAxis dataKey="name" tick={{ fill: '#cbd5e1', fontSize: 11 }} />
              <YAxis tick={{ fill: '#8b97ad', fontSize: 11 }} tickFormatter={(v) => `${Math.round(Number(v))}€`} />
              <Tooltip cursor={{ fill: 'rgba(255,255,255,.04)' }} contentStyle={tooltipStyle} formatter={(v: any) => [euro(Number(v)), 'Kosten']} />
              <Bar dataKey="cost" radius={[6, 6, 0, 0]} fill="#22d3ee" />
            </BarChart>
          </ResponsiveContainer>
        </GlowCard>
      </div>
    </div>
  )
}

import { useEffect, useState } from 'react'
import GlowCard from '../components/GlowCard'
import { api, ScrapEvent, catColor, euro } from '../api'
import { FileText, Trash2, ChevronRight, CheckCircle2 } from 'lucide-react'

export default function HistorieView({
  version, onOpen, onChange,
}: { version: number; onOpen: (e: ScrapEvent) => void; onChange: () => void }) {
  const [events, setEvents] = useState<ScrapEvent[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setLoading(true)
    api.events().then(setEvents).catch(() => {}).finally(() => setLoading(false))
  }, [version])

  const del = async (e: ScrapEvent, ev: React.MouseEvent) => {
    ev.stopPropagation()
    if (!confirm(`Vorfall ${e.part_no} löschen?`)) return
    await api.deleteEvent(e.id); onChange()
  }

  return (
    <div>
      <h1 className="text-2xl font-bold mb-1">Ausschuss-Historie</h1>
      <p className="mb-6" style={{ color: 'var(--muted)' }}>{events.length} Vorfälle — lückenlos für IATF-Audit.</p>
      <GlowCard className="p-0 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr style={{ color: 'var(--muted)' }} className="text-left">
                <th className="p-3 font-medium">Datum</th>
                <th className="p-3 font-medium">Teil</th>
                <th className="p-3 font-medium">Maschine</th>
                <th className="p-3 font-medium">Ursache</th>
                <th className="p-3 font-medium text-right">Menge</th>
                <th className="p-3 font-medium text-right">Wert</th>
                <th className="p-3 font-medium">8D</th>
                <th className="p-3"></th>
              </tr>
            </thead>
            <tbody>
              {events.map((e) => (
                <tr key={e.id} onClick={() => onOpen(e)} className="cursor-pointer hover:bg-white/5" style={{ borderTop: '1px solid var(--glass-border)' }}>
                  <td className="p-3 whitespace-nowrap">{e.created_at.slice(0, 10)}</td>
                  <td className="p-3"><div className="font-semibold">{e.part_no}</div><div style={{ color: 'var(--muted)', fontSize: 12 }}>{e.part_name}</div></td>
                  <td className="p-3 whitespace-nowrap">{e.machine_code}</td>
                  <td className="p-3"><span className="badge" style={catColor(e.cause_category)}>{e.cause_name}</span></td>
                  <td className="p-3 text-right">{e.quantity}</td>
                  <td className="p-3 text-right font-semibold">{euro(e.total_cost)}</td>
                  <td className="p-3">{e.has_report ? <CheckCircle2 size={18} color="#34d399" /> : <FileText size={16} color="#8b97ad" />}</td>
                  <td className="p-3">
                    <div className="flex items-center justify-end gap-1">
                      <button className="btn" style={{ padding: '6px 8px' }} onClick={(ev) => del(e, ev)} title="Löschen"><Trash2 size={15} /></button>
                      <ChevronRight size={16} color="#8b97ad" />
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {!loading && events.length === 0 && (
          <div className="p-8 text-center" style={{ color: 'var(--muted)' }}>Noch keine Vorfälle erfasst.</div>
        )}
      </GlowCard>
    </div>
  )
}

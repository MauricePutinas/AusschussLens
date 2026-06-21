import { useEffect, useState } from 'react'
import GlowCard from '../components/GlowCard'
import { api, ScrapEvent, Report, ReportData, euro } from '../api'
import { Brain, FileDown, RefreshCw, ArrowLeft, Loader2, AlertTriangle } from 'lucide-react'

const DISC: { d: string; title: string; key: keyof ReportData | 'd4'; accent: string }[] = [
  { d: 'D1', title: 'Team', key: 'd1_team', accent: '#22d3ee' },
  { d: 'D2', title: 'Problembeschreibung', key: 'd2_problem', accent: '#38bdf8' },
  { d: 'D3', title: 'Sofortmaßnahmen', key: 'd3_sofort', accent: '#f59e0b' },
  { d: 'D4', title: 'Ursachenanalyse · 5-Why', key: 'd4', accent: '#a855f7' },
  { d: 'D5', title: 'Abstellmaßnahmen', key: 'd5_abstell', accent: '#10b981' },
  { d: 'D6', title: 'Wirksamkeitsprüfung', key: 'd6_wirksamkeit', accent: '#38bdf8' },
  { d: 'D7', title: 'Vorbeugung / Lessons Learned', key: 'd7_praevention', accent: '#22d3ee' },
  { d: 'D8', title: 'Würdigung des Teams', key: 'd8_wuerdigung', accent: '#a855f7' },
]

function renderBody(key: keyof ReportData | 'd4', d: ReportData) {
  if (key === 'd4') {
    return (
      <div>
        <p className="mb-3"><b>{d.d4_ursache}</b></p>
        <ol className="space-y-2">
          {d.d4_five_whys.map((w, i) => (
            <li key={i} className="text-sm">
              <div style={{ color: '#c084fc' }}>{i + 1}. {w.frage}</div>
              <div style={{ color: 'var(--muted)' }}>→ {w.antwort}</div>
            </li>
          ))}
        </ol>
      </div>
    )
  }
  const val = d[key]
  if (Array.isArray(val)) {
    return (
      <ul className="space-y-1 text-sm">
        {val.map((x, i) => (
          <li key={i} className="flex gap-2"><span style={{ color: '#22d3ee' }}>▹</span><span>{String(x)}</span></li>
        ))}
      </ul>
    )
  }
  return <p className="text-sm">{String(val)}</p>
}

export default function ReportView({
  event, provider, onBack, onChange,
}: { event: ScrapEvent; provider: string; onBack: () => void; onChange: () => void }) {
  const [report, setReport] = useState<Report | null>(null)
  const [loading, setLoading] = useState(true)
  const [busy, setBusy] = useState(false)
  const live = provider.startsWith('anthropic')

  useEffect(() => {
    setLoading(true)
    api.getReport(event.id).then(setReport).catch(() => setReport(null)).finally(() => setLoading(false))
  }, [event.id])

  const generate = async () => {
    setBusy(true)
    try { const r = await api.generateReport(event.id); setReport(r); onChange() }
    catch { /* ignore */ }
    finally { setBusy(false) }
  }

  const d = report?.data

  return (
    <div>
      <button className="btn mb-4" onClick={onBack}><ArrowLeft size={16} /> Zurück</button>

      <GlowCard glow="cyan" className="p-5 mb-5">
        <div className="flex flex-col md:flex-row gap-5">
          {event.photo_url
            ? <img src={event.photo_url} alt="Ausschussteil" className="rounded-xl object-cover" style={{ width: 160, height: 120 }} />
            : <div className="rounded-xl flex items-center justify-center" style={{ width: 160, height: 120, background: 'rgba(255,255,255,.03)', border: '1px solid var(--glass-border)', color: 'var(--muted)', fontSize: 12 }}>kein Foto</div>}
          <div className="flex-1">
            <div className="text-xs" style={{ color: 'var(--muted)' }}>{event.part_no} · {event.machine_name}</div>
            <h1 className="text-2xl font-bold">{event.part_name || event.part_no}</h1>
            <div className="mt-1" style={{ color: 'var(--muted)' }}>
              {event.cause_name} · {event.quantity} Stk · <span className="text-grad font-semibold">{euro(event.total_cost)}</span>
            </div>
          </div>
          {report && (
            <div className="flex flex-col gap-2 justify-center">
              <a className="btn btn-primary" href={api.pdfUrl(event.id)} target="_blank" rel="noreferrer"><FileDown size={18} /> PDF</a>
              <button className="btn" onClick={generate} disabled={busy}>
                {busy ? <Loader2 className="animate-spin" size={16} /> : <RefreshCw size={16} />} Neu generieren
              </button>
            </div>
          )}
        </div>
      </GlowCard>

      {loading && <div style={{ color: 'var(--muted)' }}>Lade…</div>}

      {!loading && !report && (
        <GlowCard glow="violet" className="p-10 text-center">
          <Brain size={46} color="#a855f7" className="mx-auto mb-4" />
          <h2 className="text-xl font-bold mb-1">8D-Report erzeugen</h2>
          <p className="mb-6" style={{ color: 'var(--muted)' }}>
            {live ? 'Claude' : 'Der Generator'} schreibt aus diesem Vorfall einen vollständigen D1–D8-Report inkl. 5-Why — in Sekunden.
          </p>
          <button className="btn btn-violet" style={{ padding: '14px 26px', fontSize: 16 }} onClick={generate} disabled={busy}>
            {busy ? <><Loader2 className="animate-spin" size={20} /> generiere…</> : <><Brain size={20} /> 8D-Report generieren</>}
          </button>
        </GlowCard>
      )}

      {!loading && report && d && (
        <div>
          <div className="flex items-center justify-between flex-wrap gap-2 mb-3">
            <div>
              <span className="badge" style={{ background: 'rgba(34,211,238,.15)', color: '#67e8f9', border: '1px solid rgba(34,211,238,.3)' }}>{d.report_no}</span>
              <span className="ml-2 font-semibold">{d.titel}</span>
            </div>
            <span className="badge" style={{ background: live ? 'rgba(168,85,247,.15)' : 'rgba(139,151,173,.15)', color: live ? '#d8b4fe' : '#8b97ad', border: '1px solid var(--glass-border)' }}>
              {live ? 'KI: Claude' : 'KI: Mock-Entwurf'}
            </span>
          </div>

          {d._warnung && (
            <div className="badge mb-3" style={{ background: 'rgba(245,158,11,.15)', color: '#fcd34d', border: '1px solid rgba(245,158,11,.4)', padding: '6px 10px' }}>
              <AlertTriangle size={14} /> {d._warnung}
            </div>
          )}

          <div className="grid md:grid-cols-2 gap-4">
            {DISC.map((disc) => (
              <GlowCard key={disc.d} className="p-4">
                <div className="flex items-center gap-2 mb-2">
                  <span className="badge" style={{ background: disc.accent + '22', color: disc.accent, border: `1px solid ${disc.accent}55` }}>{disc.d}</span>
                  <span className="font-semibold">{disc.title}</span>
                </div>
                {renderBody(disc.key, d)}
              </GlowCard>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

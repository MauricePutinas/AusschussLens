import { useEffect, useMemo, useState } from 'react'
import GlowCard from '../components/GlowCard'
import { api, Machine, Cause, ScrapEvent, euro } from '../api'
import { Camera, Send, Loader2 } from 'lucide-react'

export default function ErfassenView({ onCreated }: { onCreated: (e: ScrapEvent) => void }) {
  const [machines, setMachines] = useState<Machine[]>([])
  const [causes, setCauses] = useState<Cause[]>([])
  const [form, setForm] = useState({
    part_no: '', part_name: '', machine_id: '', cause_id: '', quantity: '1', unit_cost: '0', note: '',
  })
  const [photo, setPhoto] = useState<File | null>(null)
  const [preview, setPreview] = useState('')
  const [busy, setBusy] = useState(false)
  const [err, setErr] = useState('')

  useEffect(() => {
    api.machines().then(setMachines).catch(() => {})
    api.causes().then(setCauses).catch(() => {})
  }, [])

  const total = useMemo(() => {
    const q = parseFloat(form.quantity || '0'), c = parseFloat(form.unit_cost || '0')
    return (isNaN(q) ? 0 : q) * (isNaN(c) ? 0 : c)
  }, [form.quantity, form.unit_cost])

  const set = (k: string, v: string) => setForm((f) => ({ ...f, [k]: v }))
  const onPhoto = (f: File | null) => { setPhoto(f); setPreview(f ? URL.createObjectURL(f) : '') }

  const grouped = useMemo(() => causes.reduce((acc: Record<string, Cause[]>, c) => {
    (acc[c.category] ??= []).push(c); return acc
  }, {}), [causes])

  const submit = async (e: React.FormEvent) => {
    e.preventDefault(); setErr('')
    if (!form.part_no || !form.machine_id || !form.cause_id) {
      setErr('Sach-Nr., Maschine und Ursache sind Pflichtfelder.'); return
    }
    setBusy(true)
    try {
      const fd = new FormData()
      Object.entries(form).forEach(([k, v]) => { if (v !== '') fd.append(k, v) })
      if (photo) fd.append('photo', photo)
      const ev = await api.createEvent(fd)
      onCreated(ev)
    } catch (e: any) {
      setErr('Speichern fehlgeschlagen: ' + e.message)
    } finally { setBusy(false) }
  }

  return (
    <div>
      <h1 className="text-2xl font-bold mb-1">Ausschuss erfassen</h1>
      <p className="mb-6" style={{ color: 'var(--muted)' }}>Foto, Maschine, Ursache — der Rest wird zum 8D-Report.</p>
      <form onSubmit={submit} className="grid md:grid-cols-3 gap-5">
        <GlowCard glow="cyan" className="p-5 md:col-span-1">
          <label>Foto des Ausschussteils</label>
          <label className="block cursor-pointer">
            <div
              className="rounded-xl border border-dashed flex items-center justify-center overflow-hidden"
              style={{ borderColor: 'var(--glass-border)', height: 220, background: 'rgba(255,255,255,.02)' }}
            >
              {preview
                ? <img src={preview} alt="Vorschau" className="object-cover w-full h-full" />
                : <div className="text-center" style={{ color: 'var(--muted)' }}><Camera size={34} className="mx-auto mb-2" />Foto wählen / aufnehmen</div>}
            </div>
            <input type="file" accept="image/*" capture="environment" className="hidden" onChange={(e) => onPhoto(e.target.files?.[0] || null)} />
          </label>
        </GlowCard>

        <GlowCard className="p-5 md:col-span-2 grid sm:grid-cols-2 gap-4 self-start">
          <div><label>Sach-Nr. *</label><input className="input" value={form.part_no} onChange={(e) => set('part_no', e.target.value)} placeholder="z.B. ST-1042" /></div>
          <div><label>Teilebezeichnung</label><input className="input" value={form.part_name} onChange={(e) => set('part_name', e.target.value)} placeholder="Kontaktfeder 0,8mm" /></div>
          <div>
            <label>Maschine *</label>
            <select className="input" value={form.machine_id} onChange={(e) => set('machine_id', e.target.value)}>
              <option value="">— wählen —</option>
              {machines.map((m) => <option key={m.id} value={m.id}>{m.code} · {m.name}</option>)}
            </select>
          </div>
          <div>
            <label>Ursache *</label>
            <select className="input" value={form.cause_id} onChange={(e) => set('cause_id', e.target.value)}>
              <option value="">— wählen —</option>
              {Object.entries(grouped).map(([cat, list]) => (
                <optgroup key={cat} label={cat}>
                  {list.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
                </optgroup>
              ))}
            </select>
          </div>
          <div><label>Menge (Stk)</label><input className="input" type="number" min="0" value={form.quantity} onChange={(e) => set('quantity', e.target.value)} /></div>
          <div><label>Stückkosten (€)</label><input className="input" type="number" min="0" step="0.01" value={form.unit_cost} onChange={(e) => set('unit_cost', e.target.value)} /></div>
          <div className="sm:col-span-2"><label>Beobachtung / Notiz</label><textarea className="input" rows={2} value={form.note} onChange={(e) => set('note', e.target.value)} placeholder="Was ist aufgefallen?" /></div>
          <div className="sm:col-span-2 flex items-center justify-between flex-wrap gap-3">
            <div className="text-sm" style={{ color: 'var(--muted)' }}>Ausschusswert: <span className="text-grad font-bold text-lg">{euro(total)}</span></div>
            <button className="btn btn-primary" disabled={busy}>
              {busy ? <Loader2 className="animate-spin" size={18} /> : <Send size={18} />} Erfassen &amp; 8D starten
            </button>
          </div>
          {err && <div className="sm:col-span-2 badge" style={{ background: 'rgba(239,68,68,.15)', color: '#fca5a5', border: '1px solid rgba(239,68,68,.4)', padding: '8px 12px' }}>{err}</div>}
        </GlowCard>
      </form>
    </div>
  )
}

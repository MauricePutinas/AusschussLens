// API-Client + Typen fuer AusschussLens

export interface Machine { id: number; code: string; name: string; area?: string }
export interface Cause { id: number; name: string; category: string }

export interface ScrapEvent {
  id: number
  created_at: string
  part_no: string
  part_name?: string | null
  machine_id: number
  cause_id: number
  quantity: number
  unit_cost: number
  total_cost: number
  photo_path?: string | null
  photo_url?: string | null
  note?: string | null
  status: string
  machine_name?: string
  machine_code?: string
  machine_area?: string
  cause_name?: string
  cause_category?: string
  has_report?: boolean
}

export interface Why { frage: string; antwort: string }

export interface ReportData {
  report_no: string
  titel: string
  d1_team: string[]
  d2_problem: string
  d3_sofort: string[]
  d4_ursache: string
  d4_five_whys: Why[]
  d5_abstell: string[]
  d6_wirksamkeit: string
  d7_praevention: string[]
  d8_wuerdigung: string
  _warnung?: string
}

export interface Report {
  id: number
  event_id: number
  created_at: string
  report_no: string
  provider: string
  data: ReportData
}

export interface CauseStat { name: string; category: string; cost: number; qty: number; events: number }
export interface MachineStat { code: string; name: string; cost: number; qty: number; events: number }

export interface Analytics {
  total_cost: number
  total_qty: number
  event_count: number
  open_count: number
  by_cause: CauseStat[]
  by_machine: MachineStat[]
  top_cause?: CauseStat
  top_machine?: MachineStat
  top_cause_share: number
  top_machine_share: number
}

async function J<T>(r: Response): Promise<T> {
  if (!r.ok) throw new Error(`HTTP ${r.status}`)
  return r.json() as Promise<T>
}

export const api = {
  health: () => fetch('/api/health').then(J<{ status: string; llm_provider: string; model?: string }>),
  machines: () => fetch('/api/machines').then(J<Machine[]>),
  causes: () => fetch('/api/causes').then(J<Cause[]>),
  events: () => fetch('/api/events').then(J<ScrapEvent[]>),
  createEvent: (fd: FormData) => fetch('/api/events', { method: 'POST', body: fd }).then(J<ScrapEvent>),
  deleteEvent: (id: number) => fetch(`/api/events/${id}`, { method: 'DELETE' }).then(J<{ deleted: number }>),
  getReport: (id: number) => fetch(`/api/events/${id}/report`).then(J<Report>),
  generateReport: (id: number) => fetch(`/api/events/${id}/report`, { method: 'POST' }).then(J<Report>),
  analytics: () => fetch('/api/analytics').then(J<Analytics>),
  pdfUrl: (id: number) => `/api/events/${id}/report/pdf`,
}

// Farbschema pro 6M-Kategorie (fuer Badges/Charts)
export function catColor(cat?: string): { background: string; color: string; border: string } {
  const m: Record<string, [string, string]> = {
    Maschine: ['rgba(34,211,238,.15)', '#67e8f9'],
    Material: ['rgba(245,158,11,.15)', '#fcd34d'],
    Mensch: ['rgba(168,85,247,.15)', '#d8b4fe'],
    Methode: ['rgba(16,185,129,.15)', '#6ee7b7'],
    Messung: ['rgba(56,189,248,.15)', '#7dd3fc'],
    Mitwelt: ['rgba(148,163,184,.15)', '#cbd5e1'],
  }
  const [bg, fg] = m[cat || ''] || ['rgba(148,163,184,.15)', '#cbd5e1']
  return { background: bg, color: fg, border: `1px solid ${fg}33` }
}

export function catHex(cat?: string): string {
  return ({
    Maschine: '#22d3ee', Material: '#f59e0b', Mensch: '#a855f7',
    Methode: '#10b981', Messung: '#38bdf8', Mitwelt: '#94a3b8',
  } as Record<string, string>)[cat || ''] || '#94a3b8'
}

export const euro = (n: number, max = 2) =>
  (n || 0).toLocaleString('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: max })

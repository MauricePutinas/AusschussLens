import { ReactNode } from 'react'

export default function StatCard({
  label, value, sub, icon,
}: { label: string; value: ReactNode; sub?: string; icon?: ReactNode }) {
  return (
    <div className="glass p-4">
      <div className="flex items-center justify-between">
        <span className="text-[11px] uppercase tracking-wide" style={{ color: 'var(--muted)' }}>{label}</span>
        {icon}
      </div>
      <div className="text-2xl font-bold mt-2">{value}</div>
      {sub && <div className="text-xs mt-1" style={{ color: 'var(--muted)' }}>{sub}</div>}
    </div>
  )
}

import { ReactNode } from 'react'

export default function GlowCard({
  children, className = '', glow,
}: { children: ReactNode; className?: string; glow?: 'cyan' | 'violet' }) {
  const g = glow === 'cyan' ? 'glow-cyan' : glow === 'violet' ? 'glow-violet' : ''
  return <div className={`glass ${g} ${className}`}>{children}</div>
}

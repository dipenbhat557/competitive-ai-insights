export default function ProgressBar({ value, max = 100, className = '' }: { value: number; max?: number; className?: string }) {
  const pct = Math.min(100, Math.max(0, (value / max) * 100))
  return (
    <div className={`h-2 rounded-full bg-slate-800 ${className}`}>
      <div className="h-full rounded-full bg-emerald-400 transition-all" style={{ width: `${pct}%` }} />
    </div>
  )
}

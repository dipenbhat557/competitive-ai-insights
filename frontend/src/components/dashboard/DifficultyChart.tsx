'use client'

interface DifficultyData {
  easy: number
  medium: number
  hard: number
}

export default function DifficultyChart({ data, total }: { data: DifficultyData; total: number }) {
  const segments = [
    { label: 'Easy', count: data.easy, color: '#34d399', bg: 'bg-emerald-400' },
    { label: 'Medium', count: data.medium, color: '#fbbf24', bg: 'bg-amber-400' },
    { label: 'Hard', count: data.hard, color: '#f87171', bg: 'bg-red-400' },
  ]

  const size = 180
  const strokeWidth = 20
  const radius = (size - strokeWidth) / 2
  const circumference = 2 * Math.PI * radius

  let offset = 0
  const arcs = segments.map((seg) => {
    const pct = total > 0 ? seg.count / total : 0
    const dashLength = pct * circumference
    const dashOffset = -offset
    offset += dashLength
    return { ...seg, dashLength, dashOffset }
  })

  return (
    <div className="card">
      <h3 className="text-lg font-semibold text-white">Difficulty Breakdown</h3>
      <div className="mt-4 flex items-center justify-center gap-8">
        <div className="relative">
          <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} className="-rotate-90">
            <circle
              cx={size / 2} cy={size / 2} r={radius}
              fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth={strokeWidth}
            />
            {arcs.map((arc, i) => (
              <circle
                key={i}
                cx={size / 2} cy={size / 2} r={radius}
                fill="none"
                stroke={arc.color}
                strokeWidth={strokeWidth}
                strokeDasharray={`${arc.dashLength} ${circumference - arc.dashLength}`}
                strokeDashoffset={arc.dashOffset}
                strokeLinecap="round"
                className="transition-all duration-700"
              />
            ))}
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className="text-3xl font-bold text-white">{total}</span>
            <span className="text-xs text-slate-400">solved</span>
          </div>
        </div>
        <div className="space-y-3">
          {segments.map((seg) => (
            <div key={seg.label} className="flex items-center gap-3">
              <div className={`h-3 w-3 rounded-full ${seg.bg}`} />
              <div>
                <p className="text-sm font-medium text-white">{seg.count}</p>
                <p className="text-xs text-slate-400">{seg.label}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

'use client'

export default function TopicChart({ topics }: { topics: Record<string, number> }) {
  const sorted = Object.entries(topics)
    .sort(([, a], [, b]) => b - a)
    .slice(0, 12)

  const max = sorted.length > 0 ? sorted[0][1] : 1

  return (
    <div className="card">
      <h3 className="text-lg font-semibold text-white">Top Topics</h3>
      <div className="mt-4 space-y-2.5">
        {sorted.map(([name, count]) => {
          const pct = (count / max) * 100
          return (
            <div key={name} className="group">
              <div className="flex items-center justify-between text-sm">
                <span className="text-slate-300 group-hover:text-white transition">{name}</span>
                <span className="tabular-nums text-slate-400">{count}</span>
              </div>
              <div className="mt-1 h-1.5 rounded-full bg-slate-800">
                <div
                  className="h-full rounded-full bg-gradient-to-r from-emerald-500 to-emerald-300 transition-all duration-700"
                  style={{ width: `${pct}%` }}
                />
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

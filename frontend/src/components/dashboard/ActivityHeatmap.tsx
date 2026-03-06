'use client'

export default function ActivityHeatmap({ calendar }: { calendar: Record<string, number> }) {
  // Build last 20 weeks of data
  const today = new Date()
  const weeks = 20
  const totalDays = weeks * 7

  const days: { date: string; count: number; dayOfWeek: number }[] = []
  for (let i = totalDays - 1; i >= 0; i--) {
    const d = new Date(today)
    d.setDate(d.getDate() - i)
    const ts = Math.floor(d.getTime() / 1000).toString()
    // LeetCode uses unix timestamps as keys
    const count = calendar[ts] || 0
    days.push({ date: d.toISOString().split('T')[0], count, dayOfWeek: d.getDay() })
  }

  const maxCount = Math.max(1, ...days.map(d => d.count))

  function getColor(count: number) {
    if (count === 0) return 'bg-slate-800/60'
    const intensity = count / maxCount
    if (intensity < 0.25) return 'bg-emerald-900/60'
    if (intensity < 0.5) return 'bg-emerald-700/70'
    if (intensity < 0.75) return 'bg-emerald-500/80'
    return 'bg-emerald-400'
  }

  // Group into weeks
  const weekGroups: typeof days[] = []
  for (let i = 0; i < days.length; i += 7) {
    weekGroups.push(days.slice(i, i + 7))
  }

  const totalSubmissions = days.reduce((s, d) => s + d.count, 0)
  const activeDays = days.filter(d => d.count > 0).length

  return (
    <div className="card">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-white">Activity</h3>
        <div className="flex gap-4 text-xs text-slate-400">
          <span><span className="font-medium text-white">{totalSubmissions}</span> submissions</span>
          <span><span className="font-medium text-white">{activeDays}</span> active days</span>
        </div>
      </div>
      <div className="mt-4 flex gap-[3px] overflow-x-auto pb-1">
        {weekGroups.map((week, wi) => (
          <div key={wi} className="flex flex-col gap-[3px]">
            {week.map((day, di) => (
              <div
                key={di}
                className={`h-3 w-3 rounded-sm ${getColor(day.count)} transition-colors`}
                title={`${day.date}: ${day.count} submission${day.count !== 1 ? 's' : ''}`}
              />
            ))}
          </div>
        ))}
      </div>
      <div className="mt-2 flex items-center justify-end gap-1 text-xs text-slate-500">
        <span>Less</span>
        <div className="h-3 w-3 rounded-sm bg-slate-800/60" />
        <div className="h-3 w-3 rounded-sm bg-emerald-900/60" />
        <div className="h-3 w-3 rounded-sm bg-emerald-700/70" />
        <div className="h-3 w-3 rounded-sm bg-emerald-500/80" />
        <div className="h-3 w-3 rounded-sm bg-emerald-400" />
        <span>More</span>
      </div>
    </div>
  )
}

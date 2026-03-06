'use client'

export default function ActivityHeatmap({ calendar }: { calendar: Record<string, number> }) {
  const today = new Date()
  const weeks = 20
  const totalDays = weeks * 7

  const days: { date: string; count: number; dayOfWeek: number }[] = []
  for (let i = totalDays - 1; i >= 0; i--) {
    const d = new Date(today)
    d.setDate(d.getDate() - i)
    const ts = Math.floor(d.getTime() / 1000).toString()
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

  const weekGroups: typeof days[] = []
  for (let i = 0; i < days.length; i += 7) {
    weekGroups.push(days.slice(i, i + 7))
  }

  const totalSubmissions = days.reduce((s, d) => s + d.count, 0)
  const activeDays = days.filter(d => d.count > 0).length

  return (
    <div className="card">
      <div className="flex flex-col gap-1 sm:flex-row sm:items-center sm:justify-between">
        <h3 className="text-base font-semibold text-white sm:text-lg">Activity</h3>
        <div className="flex gap-3 text-xs text-slate-400">
          <span><span className="font-medium text-white">{totalSubmissions}</span> submissions</span>
          <span><span className="font-medium text-white">{activeDays}</span> active days</span>
        </div>
      </div>
      <div className="mt-4 overflow-x-auto pb-1">
        <div className="flex gap-[3px]" style={{ minWidth: 'max-content' }}>
          {weekGroups.map((week, wi) => (
            <div key={wi} className="flex flex-col gap-[3px]">
              {week.map((day, di) => (
                <div
                  key={di}
                  className={`h-2.5 w-2.5 rounded-sm sm:h-3 sm:w-3 ${getColor(day.count)} transition-colors`}
                  title={`${day.date}: ${day.count} submission${day.count !== 1 ? 's' : ''}`}
                />
              ))}
            </div>
          ))}
        </div>
      </div>
      <div className="mt-2 flex items-center justify-end gap-1 text-[10px] text-slate-500 sm:text-xs">
        <span>Less</span>
        <div className="h-2.5 w-2.5 rounded-sm bg-slate-800/60 sm:h-3 sm:w-3" />
        <div className="h-2.5 w-2.5 rounded-sm bg-emerald-900/60 sm:h-3 sm:w-3" />
        <div className="h-2.5 w-2.5 rounded-sm bg-emerald-700/70 sm:h-3 sm:w-3" />
        <div className="h-2.5 w-2.5 rounded-sm bg-emerald-500/80 sm:h-3 sm:w-3" />
        <div className="h-2.5 w-2.5 rounded-sm bg-emerald-400 sm:h-3 sm:w-3" />
        <span>More</span>
      </div>
    </div>
  )
}

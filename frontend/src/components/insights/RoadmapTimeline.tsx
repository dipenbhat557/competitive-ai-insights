import Card from '@/components/ui/Card'

interface RoadmapPhase {
  range: string
  focus: string
  actions: string[]
}

interface Props {
  roadmap: RoadmapPhase[]
}

export default function RoadmapTimeline({ roadmap }: Props) {
  if (!roadmap || roadmap.length === 0) return null

  return (
    <Card>
      <h2 className="text-xl font-semibold text-white">Improvement Roadmap</h2>
      <div className="mt-6 grid gap-4 md:grid-cols-3">
        {roadmap.map((phase, i) => (
          <div key={i} className="rounded-2xl border border-white/10 bg-slate-950/60 p-4">
            <p className="text-xs font-semibold uppercase tracking-widest text-emerald-300">{phase.range}</p>
            <h4 className="mt-2 text-base font-semibold text-white">{phase.focus}</h4>
            <ul className="mt-3 space-y-2 text-sm text-slate-300">
              {phase.actions.map((action, j) => (
                <li key={j} className="flex gap-2">
                  <span className="text-emerald-400">&#x2022;</span>
                  {action}
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    </Card>
  )
}

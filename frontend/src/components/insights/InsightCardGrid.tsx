import Card from '@/components/ui/Card'

interface Props {
  strengths: Array<{ topic: string; score: number; detail: string }>
  weaknesses: Array<{ topic: string; score: number; detail: string }>
}

export default function InsightCardGrid({ strengths, weaknesses }: Props) {
  return (
    <div className="grid gap-6 lg:grid-cols-2">
      <Card>
        <h2 className="text-lg font-semibold text-emerald-400">Strengths</h2>
        <div className="mt-4 space-y-3">
          {strengths?.map((s, i) => (
            <div key={i} className="rounded-xl border border-white/10 bg-slate-950/60 p-4">
              <div className="flex items-center justify-between">
                <span className="font-medium text-white">{s.topic}</span>
                <span className="text-sm text-emerald-400">{s.score}%</span>
              </div>
              <p className="mt-1 text-sm text-slate-400">{s.detail}</p>
            </div>
          ))}
        </div>
      </Card>
      <Card>
        <h2 className="text-lg font-semibold text-amber-400">Areas to Improve</h2>
        <div className="mt-4 space-y-3">
          {weaknesses?.map((w, i) => (
            <div key={i} className="rounded-xl border border-white/10 bg-slate-950/60 p-4">
              <div className="flex items-center justify-between">
                <span className="font-medium text-white">{w.topic}</span>
                <span className="text-sm text-amber-400">{w.score}%</span>
              </div>
              <p className="mt-1 text-sm text-slate-400">{w.detail}</p>
            </div>
          ))}
        </div>
      </Card>
    </div>
  )
}

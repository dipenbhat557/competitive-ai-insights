import ProgressBar from '@/components/ui/ProgressBar'

interface Props {
  strengths: Array<{ topic: string; score: number }>
}

export default function TopicCoverageChart({ strengths }: Props) {
  return (
    <div className="card">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-white">Topic Coverage</h3>
        <span className="text-xs uppercase tracking-widest text-slate-500">Percent</span>
      </div>
      <ul className="mt-6 space-y-4">
        {strengths?.map((s, i) => (
          <li key={i}>
            <div className="flex items-center justify-between text-sm text-slate-300">
              <span>{s.topic}</span>
              <span>{s.score}%</span>
            </div>
            <ProgressBar value={s.score} className="mt-2" />
          </li>
        ))}
      </ul>
    </div>
  )
}

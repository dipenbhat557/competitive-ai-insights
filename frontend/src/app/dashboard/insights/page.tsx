'use client'

import { useInsights } from '@/lib/hooks/useInsights'
import Button from '@/components/ui/Button'
import Card from '@/components/ui/Card'
import InsightCardGrid from '@/components/insights/InsightCardGrid'
import TopicCoverageChart from '@/components/insights/TopicCoverageChart'
import StrengthRadar from '@/components/insights/StrengthRadar'
import RoadmapTimeline from '@/components/insights/RoadmapTimeline'

export default function InsightsPage() {
  const { insights, isLoading, error, generate } = useInsights()

  return (
    <div className="space-y-8">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p className="section-label">Insights</p>
          <h1 className="mt-1 text-2xl font-semibold text-white sm:text-3xl">AI Analysis</h1>
        </div>
        <Button onClick={() => generate()} disabled={isLoading} className="w-full text-sm sm:w-auto">
          {isLoading ? 'Generating...' : 'Generate Insights'}
        </Button>
      </div>

      {error && (
        <div className="rounded-lg border border-red-500/20 bg-red-500/10 p-3 text-sm text-red-400">
          {error}
        </div>
      )}

      {!insights ? (
        <Card className="py-12 text-center">
          <p className="text-lg font-semibold text-white">No insights yet</p>
          <p className="mt-2 text-sm text-slate-400">Link your platforms, scrape data, then generate AI insights.</p>
        </Card>
      ) : (
        <>
          <Card>
            <h2 className="text-xl font-semibold text-white">Summary</h2>
            <p className="mt-3 text-slate-300">{insights.summary_text}</p>
            <div className="mt-4 inline-flex items-center gap-2 rounded-full border border-emerald-500/20 bg-emerald-500/10 px-4 py-1">
              <span className="text-sm text-emerald-400">Overall Score</span>
              <span className="text-lg font-semibold text-emerald-300">{insights.overall_score}/100</span>
            </div>
          </Card>

          <InsightCardGrid strengths={insights.strengths} weaknesses={insights.weaknesses} />

          <div className="grid gap-6 lg:grid-cols-2">
            <TopicCoverageChart strengths={insights.strengths} />
            <StrengthRadar strengths={insights.strengths} />
          </div>

          <RoadmapTimeline roadmap={insights.roadmap} />

          {insights.career_recs && insights.career_recs.length > 0 && (
            <Card>
              <h2 className="text-xl font-semibold text-white">Career Recommendations</h2>
              <ul className="mt-4 space-y-3">
                {insights.career_recs.map((rec: string, i: number) => (
                  <li key={i} className="flex gap-3 text-sm text-slate-300">
                    <span className="text-emerald-400">&#x2022;</span>
                    {rec}
                  </li>
                ))}
              </ul>
            </Card>
          )}
        </>
      )}
    </div>
  )
}

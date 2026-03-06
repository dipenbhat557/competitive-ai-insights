'use client'

import { useAuth } from '@/lib/hooks/useAuth'
import { useProfile } from '@/lib/hooks/useProfile'
import StatCard from '@/components/profile/StatCard'
import PlatformBadge from '@/components/profile/PlatformBadge'
import DifficultyChart from '@/components/dashboard/DifficultyChart'
import TopicChart from '@/components/dashboard/TopicChart'
import TopicRadar from '@/components/dashboard/TopicRadar'
import ActivityHeatmap from '@/components/dashboard/ActivityHeatmap'
import Card from '@/components/ui/Card'
import Button from '@/components/ui/Button'
import { useRouter } from 'next/navigation'

function extractDifficulty(snapshots: Array<{ raw_data: Record<string, unknown> }>) {
  let easy = 0, medium = 0, hard = 0
  for (const snap of snapshots) {
    const raw = snap.raw_data || {}
    const profile = raw.profile as Record<string, unknown> | undefined
    const matched = profile?.matchedUser as Record<string, unknown> | undefined
    const stats = matched?.submitStatsGlobal as Record<string, unknown> | undefined
    const acList = (stats?.acSubmissionNum || []) as Array<{ difficulty: string; count: number }>
    for (const ac of acList) {
      if (ac.difficulty === 'Easy') easy += ac.count
      else if (ac.difficulty === 'Medium') medium += ac.count
      else if (ac.difficulty === 'Hard') hard += ac.count
    }
  }
  return { easy, medium, hard }
}

function mergeTopics(snapshots: Array<{ topic_stats: Record<string, number> }>) {
  const merged: Record<string, number> = {}
  for (const snap of snapshots) {
    for (const [topic, count] of Object.entries(snap.topic_stats || {})) {
      merged[topic] = (merged[topic] || 0) + count
    }
  }
  return merged
}

function mergeCalendars(snapshots: Array<{ submission_calendar: Record<string, number> }>) {
  const merged: Record<string, number> = {}
  for (const snap of snapshots) {
    for (const [ts, count] of Object.entries(snap.submission_calendar || {})) {
      merged[ts] = (merged[ts] || 0) + count
    }
  }
  return merged
}

export default function DashboardPage() {
  const { user } = useAuth()
  const { profiles, latestSnapshots, isLoading, scrapeAll } = useProfile()
  const router = useRouter()

  const totalSolved = latestSnapshots.reduce((sum, s) => sum + (s?.problems_solved || 0), 0)
  const avgRating = latestSnapshots.filter(s => s?.contest_rating).reduce((sum, s, _, arr) => sum + (s?.contest_rating || 0) / arr.length, 0)
  const difficulty = extractDifficulty(latestSnapshots)
  const topics = mergeTopics(latestSnapshots)
  const calendar = mergeCalendars(latestSnapshots)
  const topicCount = Object.keys(topics).length
  const hasData = latestSnapshots.length > 0 && totalSolved > 0

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-end justify-between">
        <div>
          <p className="section-label">Dashboard</p>
          <h1 className="mt-1 text-3xl font-semibold text-white">Welcome, {user?.full_name || 'Coder'}</h1>
        </div>
        {profiles.length > 0 && (
          <Button onClick={() => scrapeAll()} disabled={isLoading} variant="secondary" className="text-sm">
            {isLoading ? 'Syncing...' : 'Sync Data'}
          </Button>
        )}
      </div>

      {/* Stat Cards */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard label="Total Solved" value={totalSolved.toLocaleString()} subtext="Across all platforms" />
        <StatCard label="Avg Rating" value={avgRating ? Math.round(avgRating).toString() : '—'} subtext={avgRating ? 'Contest rating' : 'No contests yet'} />
        <StatCard label="Topics Covered" value={topicCount.toString()} subtext="Unique categories" />
        <StatCard label="Platforms" value={profiles.length.toString()} subtext={profiles.length > 0 ? profiles.map(p => p.platform).join(', ') : 'None connected'} />
      </div>

      {/* Linked Platforms Bar */}
      {profiles.length > 0 && (
        <div className="flex items-center gap-3 rounded-xl border border-white/5 bg-slate-900/30 px-4 py-3">
          <span className="text-xs uppercase tracking-widest text-slate-500">Linked</span>
          <div className="flex flex-wrap gap-2">
            {profiles.map(p => (
              <PlatformBadge key={p.id} platform={p.platform} username={p.platform_username} />
            ))}
          </div>
          <button onClick={() => router.push('/dashboard/settings')} className="ml-auto text-xs text-slate-400 hover:text-white transition">
            + Add Platform
          </button>
        </div>
      )}

      {!hasData ? (
        /* Empty state */
        <Card className="py-16 text-center">
          <div className="mx-auto max-w-md">
            <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-emerald-500/10">
              <svg className="h-8 w-8 text-emerald-400" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M13.19 8.688a4.5 4.5 0 0 1 1.242 7.244l-4.5 4.5a4.5 4.5 0 0 1-6.364-6.364l1.757-1.757m13.35-.622 1.757-1.757a4.5 4.5 0 0 0-6.364-6.364l-4.5 4.5a4.5 4.5 0 0 0 1.242 7.244" />
              </svg>
            </div>
            <h3 className="mt-4 text-xl font-semibold text-white">Connect Your Coding Profiles</h3>
            <p className="mt-2 text-sm text-slate-400">
              Link your LeetCode, Codeforces, CodeChef, or HackerRank accounts to see your stats, AI insights, and personalized mentoring.
            </p>
            <Button className="mt-6" onClick={() => router.push('/dashboard/settings')}>
              Link a Platform
            </Button>
          </div>
        </Card>
      ) : (
        <>
          {/* Charts Row 1: Difficulty + Topics */}
          <div className="grid gap-4 lg:grid-cols-2">
            <DifficultyChart data={difficulty} total={totalSolved} />
            <TopicChart topics={topics} />
          </div>

          {/* Charts Row 2: Radar + Activity */}
          <div className="grid gap-4 lg:grid-cols-2">
            <TopicRadar topics={topics} />
            <ActivityHeatmap calendar={calendar} />
          </div>
        </>
      )}

      {/* Quick Actions */}
      <div className="grid gap-4 sm:grid-cols-2">
        <Card
          className="group cursor-pointer border-transparent transition hover:border-emerald-500/30"
          onClick={() => router.push('/dashboard/insights')}
        >
          <div className="flex items-start gap-4">
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-emerald-500/10 text-emerald-400 group-hover:bg-emerald-500/20 transition">
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 3v11.25A2.25 2.25 0 0 0 6 16.5h2.25M3.75 3h-1.5m1.5 0h16.5m0 0h1.5m-1.5 0v11.25A2.25 2.25 0 0 1 18 16.5h-2.25m-7.5 0h7.5m-7.5 0-1 3m8.5-3 1 3m0 0 .5 1.5m-.5-1.5h-9.5m0 0-.5 1.5m.75-9 3-3 2.148 2.148A12.061 12.061 0 0 1 16.5 7.605" />
              </svg>
            </div>
            <div>
              <p className="section-label">AI Insights</p>
              <h3 className="mt-1 text-lg font-semibold text-white">View Your Analysis</h3>
              <p className="mt-1 text-sm text-slate-400">Strengths, weaknesses, roadmap, and career recommendations</p>
            </div>
          </div>
        </Card>
        <Card
          className="group cursor-pointer border-transparent transition hover:border-emerald-500/30"
          onClick={() => router.push('/dashboard/chat')}
        >
          <div className="flex items-start gap-4">
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-emerald-500/10 text-emerald-400 group-hover:bg-emerald-500/20 transition">
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M20.25 8.511c.884.284 1.5 1.128 1.5 2.097v4.286c0 1.136-.847 2.1-1.98 2.193-.34.027-.68.052-1.02.072v3.091l-3-3c-1.354 0-2.694-.055-4.02-.163a2.115 2.115 0 0 1-.825-.242m9.345-8.334a2.126 2.126 0 0 0-.476-.095 48.64 48.64 0 0 0-8.048 0c-1.131.094-1.976 1.057-1.976 2.192v4.286c0 .837.46 1.58 1.155 1.951m9.345-8.334V6.637c0-1.621-1.152-3.026-2.76-3.235A48.455 48.455 0 0 0 11.25 3c-2.115 0-4.198.137-6.24.402-1.608.209-2.76 1.614-2.76 3.235v6.226c0 1.621 1.152 3.026 2.76 3.235.577.075 1.157.14 1.74.194V21l4.155-4.155" />
              </svg>
            </div>
            <div>
              <p className="section-label">AI Mentor</p>
              <h3 className="mt-1 text-lg font-semibold text-white">Chat with Your Mentor</h3>
              <p className="mt-1 text-sm text-slate-400">Personalized advice based on your coding profile</p>
            </div>
          </div>
        </Card>
      </div>
    </div>
  )
}

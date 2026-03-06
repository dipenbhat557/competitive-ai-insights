'use client'

import { useAuth } from '@/lib/hooks/useAuth'
import { useProfile } from '@/lib/hooks/useProfile'
import StatCard from '@/components/profile/StatCard'
import PlatformBadge from '@/components/profile/PlatformBadge'
import Card from '@/components/ui/Card'
import Button from '@/components/ui/Button'
import { useRouter } from 'next/navigation'

export default function DashboardPage() {
  const { user } = useAuth()
  const { profiles, latestSnapshots, isLoading, scrapeAll } = useProfile()
  const router = useRouter()

  const totalSolved = latestSnapshots.reduce((sum, s) => sum + (s?.problems_solved || 0), 0)
  const avgRating = latestSnapshots.filter(s => s?.contest_rating).reduce((sum, s, _, arr) => sum + (s?.contest_rating || 0) / arr.length, 0)

  return (
    <div className="space-y-8">
      <div>
        <p className="section-label">Dashboard</p>
        <h1 className="mt-1 text-3xl font-semibold text-white">Welcome, {user?.full_name || 'Coder'}</h1>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard label="Total Solved" value={totalSolved.toLocaleString()} subtext="Across all platforms" />
        <StatCard label="Avg Rating" value={avgRating ? Math.round(avgRating).toString() : 'N/A'} subtext="Contest rating" />
        <StatCard label="Platforms" value={profiles.length.toString()} subtext="Connected" />
        <StatCard label="Last Scraped" value={latestSnapshots[0]?.scraped_at ? new Date(latestSnapshots[0].scraped_at).toLocaleDateString() : 'Never'} subtext="Profile data" />
      </div>

      <Card>
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-white">Linked Platforms</h2>
          <div className="flex gap-2">
            <Button variant="secondary" onClick={() => router.push('/dashboard/settings')}>
              Manage
            </Button>
            <Button onClick={() => scrapeAll()} disabled={isLoading}>
              {isLoading ? 'Scraping...' : 'Refresh Data'}
            </Button>
          </div>
        </div>
        <div className="mt-4">
          {profiles.length === 0 ? (
            <p className="text-sm text-slate-400">No platforms linked yet. Go to settings to connect your LeetCode, Codeforces, CodeChef, or HackerRank profiles.</p>
          ) : (
            <div className="flex flex-wrap gap-3">
              {profiles.map(p => (
                <PlatformBadge key={p.id} platform={p.platform} username={p.platform_username} />
              ))}
            </div>
          )}
        </div>
      </Card>

      <div className="grid gap-4 sm:grid-cols-2">
        <Card className="cursor-pointer transition hover:border-emerald-500/30" onClick={() => router.push('/dashboard/insights')}>
          <p className="section-label">AI Insights</p>
          <h3 className="mt-2 text-xl font-semibold text-white">View Your Analysis</h3>
          <p className="mt-2 text-sm text-slate-400">Cross-platform strengths, weaknesses, roadmap, and career recommendations</p>
        </Card>
        <Card className="cursor-pointer transition hover:border-emerald-500/30" onClick={() => router.push('/dashboard/chat')}>
          <p className="section-label">AI Mentor</p>
          <h3 className="mt-2 text-xl font-semibold text-white">Chat with Your Mentor</h3>
          <p className="mt-2 text-sm text-slate-400">Get personalized advice based on your unified coding profile</p>
        </Card>
      </div>
    </div>
  )
}

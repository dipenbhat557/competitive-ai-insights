'use client'

import Card from '@/components/ui/Card'
import type { NormalizedAggregate } from '@/lib/types'

interface Props {
  normalized: NormalizedAggregate
}

const PLATFORM_COLORS: Record<string, string> = {
  leetcode: 'text-amber-300',
  codeforces: 'text-sky-300',
  codechef: 'text-rose-300',
  hackerrank: 'text-emerald-300',
}

const DIFFICULTY_COLOR: Record<string, string> = {
  easy: 'bg-emerald-400',
  medium: 'bg-amber-400',
  hard: 'bg-orange-400',
  expert: 'bg-rose-400',
}

export default function SkillProfile({ normalized }: Props) {
  const overallPct = normalized.rating_percentile_overall ?? 0

  const topTopics = Object.entries(normalized.canonical_topic_stats)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 8)

  const topTopicMax = topTopics[0]?.[1] || 1

  const totalDifficulty =
    Object.values(normalized.difficulty_breakdown).reduce((a, b) => a + b, 0) || 1

  const platformsWithRating = normalized.per_platform.filter(
    p => p.rating_percentile != null
  )

  return (
    <Card>
      <div className="flex items-start justify-between">
        <div>
          <p className="section-label">Unified Skill Profile</p>
          <h3 className="mt-1 text-lg font-semibold text-white">
            Cross-Platform Normalization
          </h3>
          <p className="mt-1 text-xs text-slate-500">
            Canonical topics · percentile-equivalent ratings · difficulty-weighted volume
          </p>
        </div>
        <div className="flex items-center gap-1.5 rounded-full border border-emerald-500/20 bg-emerald-500/10 px-3 py-1 text-xs text-emerald-300">
          <span className="h-1.5 w-1.5 rounded-full bg-emerald-400" />
          {normalized.coverage} canonical topics
        </div>
      </div>

      {/* Top row: percentile ring + weighted volume */}
      <div className="mt-6 grid gap-4 sm:grid-cols-3">
        <PercentileRing percentile={overallPct} />

        <div className="sm:col-span-2 space-y-3">
          <div className="rounded-xl border border-white/10 bg-slate-900/40 p-4">
            <p className="text-[11px] uppercase tracking-widest text-slate-500">
              Weighted Problem Volume
            </p>
            <p className="mt-1 text-2xl font-semibold text-white">
              {normalized.total_weighted_volume.toLocaleString()}
            </p>
            <p className="mt-1 text-xs text-slate-400">
              {normalized.total_problems_raw} solved · weighted by difficulty &amp; platform
            </p>
          </div>

          {platformsWithRating.length > 0 && (
            <div className="rounded-xl border border-white/10 bg-slate-900/40 p-4">
              <p className="text-[11px] uppercase tracking-widest text-slate-500">
                Per-Platform Rating Percentile
              </p>
              <div className="mt-2 space-y-2">
                {platformsWithRating.map(p => (
                  <div key={p.platform} className="flex items-center gap-2">
                    <span
                      className={`w-20 text-xs font-medium ${
                        PLATFORM_COLORS[p.platform] || 'text-slate-300'
                      }`}
                    >
                      {p.platform}
                    </span>
                    <div className="relative h-2 flex-1 overflow-hidden rounded-full bg-white/5">
                      <div
                        className="absolute inset-y-0 left-0 rounded-full bg-gradient-to-r from-emerald-500 to-emerald-300"
                        style={{ width: `${Math.min(100, p.rating_percentile ?? 0)}%` }}
                      />
                    </div>
                    <span className="w-14 text-right text-xs text-slate-400">
                      {p.raw_rating ? Math.round(p.raw_rating) : '—'}
                      <span className="ml-1 text-slate-500">·</span>
                      <span className="ml-1 text-emerald-300">
                        {p.rating_percentile?.toFixed(0)}%
                      </span>
                    </span>
                  </div>
                ))}
              </div>
              <p className="mt-2 text-[11px] text-slate-500">
                Raw ratings across platforms aren&apos;t comparable (LC 1700 ≠ CF 1700). Percentile gives an
                apples-to-apples view.
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Topic distribution */}
      {topTopics.length > 0 && (
        <div className="mt-6">
          <p className="section-label">Top canonical topics</p>
          <div className="mt-3 space-y-2">
            {topTopics.map(([topic, count]) => {
              const label = normalized.topic_labels[topic] || topic
              const pct = (count / topTopicMax) * 100
              return (
                <div key={topic} className="flex items-center gap-3">
                  <span className="w-44 truncate text-sm text-slate-300">{label}</span>
                  <div className="relative h-3 flex-1 overflow-hidden rounded-full bg-white/5">
                    <div
                      className="absolute inset-y-0 left-0 rounded-full bg-gradient-to-r from-emerald-500/80 to-emerald-400"
                      style={{ width: `${pct}%` }}
                    />
                  </div>
                  <span className="w-12 text-right text-xs text-slate-400">{count}</span>
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* Difficulty mix bar */}
      {totalDifficulty > 1 && (
        <div className="mt-6">
          <p className="section-label">Difficulty mix (combined)</p>
          <div className="mt-3 flex h-3 overflow-hidden rounded-full bg-white/5">
            {(['easy', 'medium', 'hard', 'expert'] as const).map(b => {
              const v = normalized.difficulty_breakdown[b] || 0
              const pct = (v / totalDifficulty) * 100
              if (pct === 0) return null
              return (
                <div
                  key={b}
                  className={DIFFICULTY_COLOR[b]}
                  style={{ width: `${pct}%` }}
                  title={`${b}: ${v}`}
                />
              )
            })}
          </div>
          <div className="mt-2 flex flex-wrap gap-3 text-xs text-slate-400">
            {(['easy', 'medium', 'hard', 'expert'] as const).map(b => {
              const v = normalized.difficulty_breakdown[b] || 0
              if (!v) return null
              return (
                <span key={b} className="flex items-center gap-1.5">
                  <span className={`h-2 w-2 rounded-full ${DIFFICULTY_COLOR[b]}`} />
                  {b} · {v}
                </span>
              )
            })}
          </div>
        </div>
      )}
    </Card>
  )
}

function PercentileRing({ percentile }: { percentile: number }) {
  const pct = Math.max(0, Math.min(100, percentile))
  const r = 56
  const c = 2 * Math.PI * r
  const offset = c - (pct / 100) * c
  return (
    <div className="flex flex-col items-center justify-center rounded-xl border border-white/10 bg-slate-900/40 p-4">
      <div className="relative h-32 w-32">
        <svg className="h-full w-full -rotate-90" viewBox="0 0 140 140">
          <circle cx="70" cy="70" r={r} fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth="10" />
          <circle
            cx="70"
            cy="70"
            r={r}
            fill="none"
            stroke="url(#ringGrad)"
            strokeWidth="10"
            strokeLinecap="round"
            strokeDasharray={c}
            strokeDashoffset={offset}
          />
          <defs>
            <linearGradient id="ringGrad" x1="0" y1="0" x2="1" y2="1">
              <stop offset="0%" stopColor="#34d399" />
              <stop offset="100%" stopColor="#10b981" />
            </linearGradient>
          </defs>
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-3xl font-semibold text-white">{pct.toFixed(0)}</span>
          <span className="text-[10px] uppercase tracking-widest text-slate-500">percentile</span>
        </div>
      </div>
      <p className="mt-3 text-center text-xs text-slate-400">
        Best rating across linked platforms
      </p>
    </div>
  )
}

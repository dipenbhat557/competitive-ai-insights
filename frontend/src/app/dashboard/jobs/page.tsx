'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Card from '@/components/ui/Card'
import Button from '@/components/ui/Button'
import { apiClient } from '@/lib/api-client'
import type { ChatSession, JobMatch } from '@/lib/types'

export default function JobMatchesPage() {
  const router = useRouter()
  const [matches, setMatches] = useState<JobMatch[] | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [preparingKey, setPreparingKey] = useState<string | null>(null)

  const loadMatches = async () => {
    setIsLoading(true)
    setError(null)
    try {
      const data = await apiClient<JobMatch[]>(
        '/api/v1/jobs/matches?include_external=true&top_n=10'
      )
      setMatches(data)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to fetch matches')
    } finally {
      setIsLoading(false)
    }
  }

  const handlePrepare = async (match: JobMatch, key: string) => {
    setPreparingKey(key)
    try {
      const session = await apiClient<ChatSession>('/api/v1/chat/sessions', {
        method: 'POST',
        body: JSON.stringify({ title: `${match.title} Preparation` }),
      })
      const kickoff = buildKickoffPrompt(match)
      router.push(
        `/dashboard/chat?session=${session.id}&kickoff=${encodeURIComponent(kickoff)}`
      )
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to start prep session')
      setPreparingKey(null)
    }
  }

  return (
    <div className="space-y-8">
      <HeroBanner />

      {/* Action row */}
      <Card className="border-emerald-500/20 bg-gradient-to-br from-emerald-500/5 to-transparent">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="section-label">AI Job Matching</p>
            <p className="mt-1 text-sm text-slate-300">
              Live postings from internal recruiters and public boards (RemoteOK, Greenhouse), each scored by Gemini against your unified skill profile.
            </p>
          </div>
          <Button onClick={loadMatches} disabled={isLoading} className="w-full sm:w-auto">
            {isLoading ? 'Matching with AI…' : matches ? 'Refresh Matches' : 'Find My Matches'}
          </Button>
        </div>
      </Card>

      {error && (
        <div className="rounded-lg border border-red-500/20 bg-red-500/10 p-3 text-sm text-red-400">
          {error}
        </div>
      )}

      {!matches && !isLoading && !error && <EmptyState />}

      {matches && matches.length === 0 && (
        <Card className="py-12 text-center">
          <p className="text-slate-400">No suitable jobs found right now. Try refreshing in a bit.</p>
        </Card>
      )}

      {matches && matches.length > 0 && (
        <div className="space-y-4">
          {matches.map((m, idx) => {
            const key = `${m.source}-${m.job_id ?? m.title}-${idx}`
            return (
              <MatchCard
                key={key}
                match={m}
                onPrepare={() => handlePrepare(m, key)}
                preparing={preparingKey === key}
              />
            )
          })}
        </div>
      )}
    </div>
  )
}

function HeroBanner() {
  return (
    <div className="relative overflow-hidden rounded-3xl border border-white/10 bg-gradient-to-br from-emerald-500/10 via-slate-900/50 to-slate-900/0 p-6 sm:p-8">
      <div className="pointer-events-none absolute -right-20 -top-20 h-72 w-72 rounded-full bg-emerald-500/10 blur-3xl" />
      <div className="pointer-events-none absolute -bottom-32 -left-10 h-72 w-72 rounded-full bg-emerald-400/5 blur-3xl" />
      <div className="relative">
        <p className="section-label text-emerald-300">CodePulse · Job Matches</p>
        <h1 className="mt-2 max-w-2xl text-3xl font-semibold leading-tight text-white sm:text-4xl">
          From practice to placement —
          <span className="block bg-gradient-to-r from-emerald-300 to-emerald-100 bg-clip-text text-transparent">
            your competitive coding, intelligently aggregated.
          </span>
        </h1>
        <p className="mt-4 max-w-2xl text-sm text-slate-300 sm:text-base">
          We unify your LeetCode, Codeforces, CodeChef &amp; HackerRank profile into one canonical skill view, then match it to live job postings — and give you a one-click AI prep plan for every role.
        </p>

        <div className="mt-6 grid gap-3 sm:grid-cols-3">
          <PillarCard
            label="Unified Profile"
            text="One canonical view across 4 platforms — percentile ratings, not raw."
          />
          <PillarCard
            label="AI Fit Score"
            text="Gemini reasons over your profile vs. the job's actual requirements."
          />
          <PillarCard
            label="One-Click Prep"
            text="Turn any match into a tailored mentor session, instantly."
          />
        </div>
      </div>
    </div>
  )
}

function PillarCard({ label, text }: { label: string; text: string }) {
  return (
    <div className="rounded-xl border border-white/10 bg-slate-900/40 p-4">
      <p className="text-xs font-medium uppercase tracking-widest text-emerald-300">{label}</p>
      <p className="mt-2 text-sm text-slate-300">{text}</p>
    </div>
  )
}

function EmptyState() {
  return (
    <Card className="py-12 text-center">
      <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-emerald-500/10">
        <svg
          className="h-7 w-7 text-emerald-400"
          fill="none"
          viewBox="0 0 24 24"
          strokeWidth={1.5}
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z"
          />
        </svg>
      </div>
      <p className="mt-4 text-lg font-semibold text-white">Ready when you are</p>
      <p className="mt-2 text-sm text-slate-400">
        Click <span className="font-medium text-emerald-400">Find My Matches</span> to score live postings against your profile.
      </p>
    </Card>
  )
}

function MatchCard({
  match,
  onPrepare,
  preparing,
}: {
  match: JobMatch
  onPrepare: () => void
  preparing: boolean
}) {
  const score = Math.round(match.match_score)
  const scoreColor =
    score >= 75
      ? 'from-emerald-500 to-emerald-300 text-emerald-100'
      : score >= 50
      ? 'from-amber-500 to-amber-300 text-amber-100'
      : 'from-slate-500 to-slate-400 text-slate-100'
  const sourceLabel =
    match.source === 'internal'
      ? 'CodePulse'
      : match.source.replace('greenhouse:', 'Greenhouse · ').replace('remoteok', 'RemoteOK')

  return (
    <Card className="relative overflow-hidden transition hover:border-emerald-500/30">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <h3 className="text-lg font-semibold text-white">{match.title}</h3>
            <span className="rounded-full border border-white/10 bg-white/5 px-2 py-0.5 text-[11px] uppercase tracking-wide text-slate-400">
              {sourceLabel}
            </span>
          </div>
          <p className="mt-1 text-sm text-slate-400">
            {match.company || 'Internal posting'}
            {match.location ? ` · ${match.location}` : ''}
          </p>
        </div>

        <div className="flex shrink-0 items-center gap-3">
          <div
            className={`flex h-16 w-16 flex-col items-center justify-center rounded-2xl bg-gradient-to-br ${scoreColor} shadow-lg shadow-emerald-500/10`}
          >
            <span className="text-xl font-bold leading-none">{score}</span>
            <span className="mt-0.5 text-[9px] uppercase tracking-widest opacity-80">fit</span>
          </div>
        </div>
      </div>

      {match.reasoning && (
        <p className="mt-4 text-sm leading-relaxed text-slate-300">{match.reasoning}</p>
      )}

      <div className="mt-4 grid gap-4 sm:grid-cols-2">
        {match.highlights.length > 0 && (
          <div>
            <p className="section-label text-emerald-300">Why you fit</p>
            <ul className="mt-2 space-y-1 text-sm text-slate-300">
              {match.highlights.slice(0, 4).map((h, i) => (
                <li key={i} className="flex gap-2">
                  <span className="mt-0.5 text-emerald-400">+</span>
                  <span>{h}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {match.skill_gaps.length > 0 && (
          <div>
            <p className="section-label text-amber-300">Gaps to close</p>
            <div className="mt-2 flex flex-wrap gap-1.5">
              {match.skill_gaps.map((g, i) => (
                <span
                  key={i}
                  className="rounded-full border border-amber-500/20 bg-amber-500/10 px-2 py-0.5 text-xs text-amber-300"
                >
                  {g}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      {match.required_skills.length > 0 && (
        <div className="mt-4 flex flex-wrap gap-1.5">
          {match.required_skills.slice(0, 12).map((s, i) => (
            <span
              key={i}
              className="rounded-full border border-white/10 bg-white/5 px-2 py-0.5 text-xs text-slate-300"
            >
              {s}
            </span>
          ))}
        </div>
      )}

      <div className="mt-5 flex flex-col gap-2 border-t border-white/10 pt-4 sm:flex-row sm:items-center sm:justify-between">
        <p className="text-xs text-slate-500">
          One click below turns this match into a focused AI prep plan in your mentor chat.
        </p>
        <div className="flex gap-2">
          {match.apply_url && (
            <a
              href={match.apply_url}
              target="_blank"
              rel="noopener noreferrer"
              className="btn-secondary text-sm"
            >
              Apply
              <span aria-hidden> →</span>
            </a>
          )}
          <button
            onClick={onPrepare}
            disabled={preparing}
            className="btn-primary inline-flex items-center gap-1.5 text-sm disabled:opacity-60"
          >
            {preparing ? (
              <>
                <span className="h-3 w-3 animate-spin rounded-full border-2 border-white/40 border-t-white" />
                Spinning up mentor…
              </>
            ) : (
              <>
                <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z"
                  />
                </svg>
                Prepare with AI Mentor
              </>
            )}
          </button>
        </div>
      </div>
    </Card>
  )
}

function buildKickoffPrompt(m: JobMatch): string {
  const company = m.company || 'this company'
  const skills = m.required_skills.join(', ') || 'not specified'
  const gaps = m.skill_gaps.length > 0 ? m.skill_gaps.join(', ') : 'none flagged'
  const location = m.location ? `Location: ${m.location}\n` : ''
  const description = m.description
    ? `\n\nJob description (excerpt):\n${m.description.slice(0, 1500)}`
    : ''

  return `I want to prepare for this specific role using the profile data you already have on me. Please give me a focused, time-bounded preparation plan.

Role: ${m.title} at ${company}
${location}Required skills: ${skills}
Gaps you flagged earlier: ${gaps}
Current AI fit score: ${Math.round(m.match_score)}/100

Please:
1. Identify the top 3–5 weak areas I need to close before applying, using my actual canonical-topic stats.
2. Give a concrete 2-week plan, day-by-day if possible, referencing specific LeetCode / Codeforces problems by name or number.
3. Suggest 2–3 system-design or behavioral-prep items if relevant for this role.
4. Recommend 1 concrete project I could ship that would directly strengthen my application for this kind of role.
5. End with an honest read: should I apply now, or wait until I&#39;ve closed specific gaps?${description}`
}

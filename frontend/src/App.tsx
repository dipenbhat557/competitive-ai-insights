import type { FormEvent } from 'react'
import { useMemo, useState } from 'react'
import './App.css'

interface Stats {
  solved: number
  acceptance: string
  contestRating: number
  streak: number
}

interface TopicMetric {
  label: string
  value: number
}

interface ActivityPoint {
  label: string
  value: number
}

interface InsightCard {
  title: string
  summary: string
  metric: string
}

interface RoadmapItem {
  range: string
  focus: string
  actions: string[]
}

interface ChatMessage {
  id: string
  role: 'assistant' | 'user'
  content: string
}

const baselineStats: Stats = {
  solved: 0,
  acceptance: '0%',
  contestRating: 0,
  streak: 0,
}

const insightCards: InsightCard[] = [
  {
    title: 'Strength Pulse',
    summary: 'Dynamic Programming sets finish with elite accuracy and sub-15 minute cycles.',
    metric: 'DP · 92%',
  },
  {
    title: 'Gap Radar',
    summary: 'Graph problems consume 38% more time than baseline. Focus on BFS templates.',
    metric: 'Graphs · 63%',
  },
  {
    title: 'Contest Strategy',
    summary: 'Rating drops happen on the last slot. Reserve ten minutes for triage decisions.',
    metric: 'Late-game pacing',
  },
]

const roadmap: RoadmapItem[] = [
  {
    range: 'Days 1-30',
    focus: 'Rebuild rhythm',
    actions: ['Daily streak guardrails', 'Top 30 DP refresh', 'Weekend mini-contests'],
  },
  {
    range: 'Days 31-60',
    focus: 'Broaden coverage',
    actions: ['Tree/Graph alternation', 'Mid-week mock interviews', 'Topic retros every Sunday'],
  },
  {
    range: 'Days 61-90',
    focus: 'Offer readiness',
    actions: ['Company-focused playlists', 'Contest pacing drills', 'Behavioral story library'],
  },
]

function buildTopicMetrics(seed: number): TopicMetric[] {
  const base: TopicMetric[] = [
    { label: 'DP', value: 88 },
    { label: 'Graphs', value: 64 },
    { label: 'Trees', value: 72 },
    { label: 'Strings', value: 78 },
    { label: 'Greedy', value: 69 },
    { label: 'Backtracking', value: 58 },
  ]
  return base.map((metric, index) => ({
    ...metric,
    value: Math.min(100, Math.max(40, metric.value + ((seed + index * 7) % 18) - 9)),
  }))
}

function buildActivity(seed: number): ActivityPoint[] {
  const weeks = ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5', 'Week 6']
  return weeks.map((label, index) => ({
    label,
    value: 10 + ((seed + index * 5) % 15),
  }))
}

function App() {
  const [username, setUsername] = useState('')
  const [stats, setStats] = useState<Stats>(baselineStats)
  const [isReady, setIsReady] = useState(false)
  const [chatDraft, setChatDraft] = useState('')
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 'assistant-welcome',
      role: 'assistant',
      content: 'Enter a username and I will craft insights, charts, and next steps.',
    },
  ])

  const topicMetrics = useMemo(() => buildTopicMetrics(username.length || 1), [username])
  const activityTrend = useMemo(() => buildActivity(username.length || 1), [username])

  function personalizeStats(handle: string): Stats {
    const size = handle.length
    return {
      solved: 650 + size * 16,
      acceptance: `${(61 + (size % 20)).toFixed(1)}%`,
      contestRating: 1500 + size * 23,
      streak: 5 + size,
    }
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const trimmed = username.trim()
    if (!trimmed) return

    setStats(personalizeStats(trimmed))
    setIsReady(true)
    setMessages(prev => [
      ...prev,
      {
        id: `assistant-update-${Date.now()}`,
        role: 'assistant',
        content: `Insights generated for ${trimmed}. Ask for practice plans, contest pacing, or job-aligned prep.`,
      },
    ])
  }

  function handleChatSend(value: string) {
    const trimmed = value.trim()
    if (!trimmed) return

    const timestamp = Date.now()
    const reply = `Great point. Double down on ${topicMetrics[0].label} reps and keep contests around ${
      activityTrend[activityTrend.length - 1].value >= 18 ? 'mid-week' : 'weekend'
    } for best stamina.`

    setMessages(prev => [
      ...prev,
      { id: `user-${timestamp}`, role: 'user', content: trimmed },
      { id: `assistant-${timestamp}`, role: 'assistant', content: reply },
    ])
    setChatDraft('')
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-50">
      <div className="mx-auto flex w-full max-w-6xl flex-col gap-16 px-4 py-12 sm:px-6 lg:px-8">
        <HeroSection username={username} onSubmit={handleSubmit} onUsernameChange={setUsername} stats={stats} />
        {isReady ? (
          <>
            <InsightsDashboard
              username={username.trim()}
              topicMetrics={topicMetrics}
              activityTrend={activityTrend}
              insights={insightCards}
              roadmap={roadmap}
            />
            <ChatDock messages={messages} draft={chatDraft} onDraftChange={setChatDraft} onSend={handleChatSend} />
          </>
        ) : (
          <PlaceholderPanel />
        )}
      </div>
    </div>
  )
}

interface HeroSectionProps {
  username: string
  stats: Stats
  onUsernameChange: (value: string) => void
  onSubmit: (event: FormEvent<HTMLFormElement>) => void
}

function HeroSection({ username, stats, onUsernameChange, onSubmit }: HeroSectionProps) {
  return (
    <section className="space-y-10 rounded-3xl border border-white/10 bg-linear-to-br from-slate-900/80 via-slate-900 to-slate-950/60 p-8 shadow-2xl shadow-emerald-500/10">
      <div className="space-y-4">
        <p className="text-sm uppercase tracking-[0.3em] text-emerald-400">Competitive Programming AI Insights Platform</p>
        <h1 className="text-4xl font-semibold leading-tight text-white sm:text-5xl">Decode your coding journey with AI-powered clarity.</h1>
        <p className="text-lg text-slate-300">Connect a username, unlock tailored analytics, discover career fits, and chat with a focused mentor.</p>
      </div>

      <form className="flex flex-col gap-4 rounded-2xl border border-white/10 bg-white/5 p-4 sm:flex-row" onSubmit={onSubmit}>
        <label className="grow text-sm font-medium text-slate-200">
          Username
          <input
            value={username}
            onChange={event => onUsernameChange(event.target.value)}
            placeholder="Enter username"
            className="mt-1 w-full rounded-xl border border-white/10 bg-slate-900/60 px-4 py-3 text-base text-white outline-none ring-emerald-500/40 focus:ring-2"
          />
        </label>
        <button type="submit" className="rounded-xl bg-emerald-500 px-6 py-3 text-base font-semibold text-slate-950 transition hover:bg-emerald-400">
          Generate Insights
        </button>
      </form>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard label="Problems Solved" value={stats.solved.toLocaleString()} subtext="All-time" />
        <StatCard label="Acceptance Rate" value={stats.acceptance} subtext="12M submissions parsed" />
        <StatCard label="Contest Rating" value={stats.contestRating ? stats.contestRating.toString() : '0'} subtext="Top percentile" />
        <StatCard label="Current Streak" value={`${stats.streak} days`} subtext="Activity graph synced" />
      </div>
    </section>
  )
}

interface StatCardProps {
  label: string
  value: string
  subtext: string
}

function StatCard({ label, value, subtext }: StatCardProps) {
  return (
    <div className="rounded-2xl border border-white/10 bg-slate-900/50 p-4">
      <p className="text-sm text-slate-400">{label}</p>
      <p className="mt-2 text-2xl font-semibold text-white">{value}</p>
      <p className="text-xs text-slate-500">{subtext}</p>
    </div>
  )
}

interface InsightsDashboardProps {
  username: string
  topicMetrics: TopicMetric[]
  activityTrend: ActivityPoint[]
  insights: InsightCard[]
  roadmap: RoadmapItem[]
}

function InsightsDashboard({ username, topicMetrics, activityTrend, insights, roadmap }: InsightsDashboardProps) {
  return (
    <section className="space-y-8">
      <header className="space-y-1">
        <p className="text-xs uppercase tracking-[0.35em] text-emerald-400">Insights</p>
        <h2 className="text-3xl font-semibold text-white">AI summary for {username}</h2>
      </header>

      <div className="grid gap-6 lg:grid-cols-3">
        {insights.map(item => (
          <div key={item.title} className="rounded-2xl border border-white/10 bg-slate-900/40 p-6">
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-emerald-300">{item.metric}</p>
            <h3 className="mt-2 text-xl font-semibold text-white">{item.title}</h3>
            <p className="mt-3 text-sm text-slate-300">{item.summary}</p>
          </div>
        ))}
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="rounded-2xl border border-white/10 bg-slate-900/40 p-6">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-white">Topic Coverage</h3>
            <span className="text-xs uppercase tracking-[0.2em] text-slate-500">Percent</span>
          </div>
          <ul className="mt-6 space-y-4">
            {topicMetrics.map(metric => (
              <li key={metric.label}>
                <div className="flex items-center justify-between text-sm text-slate-300">
                  <span>{metric.label}</span>
                  <span>{metric.value}%</span>
                </div>
                <div className="mt-2 h-2 rounded-full bg-slate-800">
                  <div className="h-full rounded-full bg-emerald-400" style={{ width: `${metric.value}%` }} />
                </div>
              </li>
            ))}
          </ul>
        </div>

        <div className="rounded-2xl border border-white/10 bg-slate-900/40 p-6">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-white">6-week Activity</h3>
            <span className="text-xs uppercase tracking-[0.2em] text-slate-500">Sessions</span>
          </div>
          <div className="mt-6 grid grid-cols-6 items-end gap-4">
            {activityTrend.map(point => (
              <div key={point.label} className="text-center text-xs text-slate-400">
                <div className="mx-auto flex h-32 w-full items-end justify-center rounded-xl bg-slate-900/80">
                  <div className="w-8 rounded-t-lg bg-emerald-400" style={{ height: `${Math.min(100, point.value * 4)}%` }} />
                </div>
                <p className="mt-2">{point.label}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="rounded-3xl border border-white/10 bg-slate-900/40 p-6">
        <h3 className="text-lg font-semibold text-white">90-day roadmap</h3>
        <div className="mt-4 grid gap-4 md:grid-cols-3">
          {roadmap.map(stage => (
            <div key={stage.range} className="rounded-2xl border border-white/10 bg-slate-950/60 p-4">
              <p className="text-xs font-semibold uppercase tracking-[0.2em] text-emerald-300">{stage.range}</p>
              <h4 className="mt-2 text-base font-semibold text-white">{stage.focus}</h4>
              <ul className="mt-3 space-y-2 text-sm text-slate-300">
                {stage.actions.map(action => (
                  <li key={action} className="flex gap-2">
                    <span className="text-emerald-400">•</span>
                    {action}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

interface ChatDockProps {
  messages: ChatMessage[]
  draft: string
  onDraftChange: (value: string) => void
  onSend: (value: string) => void
}

function ChatDock({ messages, draft, onDraftChange, onSend }: ChatDockProps) {
  return (
    <section className="rounded-3xl border border-white/10 bg-slate-900/50 p-6">
      <header>
        <p className="text-xs uppercase tracking-[0.3em] text-emerald-400">AI Copilot</p>
        <h3 className="mt-1 text-2xl font-semibold text-white">Chat with your mentor</h3>
      </header>
      <div className="mt-6 flex flex-col gap-4">
        <div className="h-64 overflow-auto rounded-2xl border border-white/10 bg-slate-950/70 p-4">
          <ul className="space-y-3 text-sm">
            {messages.map(message => (
              <li key={message.id}>
                <p className="text-xs uppercase tracking-[0.2em] text-slate-500">{message.role}</p>
                <p className={message.role === 'assistant' ? 'mt-1 text-slate-200' : 'mt-1 text-emerald-200'}>{message.content}</p>
              </li>
            ))}
          </ul>
        </div>
        <form
          className="flex flex-col gap-3 rounded-2xl border border-white/10 bg-white/5 p-4 sm:flex-row"
          onSubmit={event => {
            event.preventDefault()
            onSend(draft)
          }}
        >
          <input
            value={draft}
            onChange={event => onDraftChange(event.target.value)}
            placeholder="Ask about practice schedules, contests, or interviews…"
            className="flex-1 rounded-xl border border-white/10 bg-slate-900/60 px-4 py-3 text-base text-white outline-none ring-emerald-500/40 focus:ring-2"
          />
          <button type="submit" className="rounded-xl bg-emerald-500 px-6 py-3 text-base font-semibold text-slate-950 transition hover:bg-emerald-400">
            Send
          </button>
        </form>
      </div>
    </section>
  )
}

function PlaceholderPanel() {
  return (
    <section className="rounded-3xl border border-dashed border-white/10 bg-slate-900/30 p-8 text-center">
      <p className="text-lg font-semibold text-white">Awaiting username</p>
      <p className="mt-2 text-sm text-slate-400">Provide any public username to unlock dummy analytics, charts, and the AI chat dock.</p>
    </section>
  )
}

export default App

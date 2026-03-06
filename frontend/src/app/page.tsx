'use client'

import { useState, FormEvent } from 'react'
import { useRouter } from 'next/navigation'
import Navbar from '@/components/layout/Navbar'
import Footer from '@/components/layout/Footer'
import StatCard from '@/components/profile/StatCard'
import PlatformBadge from '@/components/profile/PlatformBadge'
import Button from '@/components/ui/Button'
import Input from '@/components/ui/Input'

const PLATFORMS = [
  { id: 'leetcode', label: 'LeetCode', color: 'text-yellow-400' },
  { id: 'codeforces', label: 'Codeforces', color: 'text-blue-400' },
  { id: 'codechef', label: 'CodeChef', color: 'text-orange-400' },
  { id: 'hackerrank', label: 'HackerRank', color: 'text-green-400' },
]

export default function LandingPage() {
  const router = useRouter()
  const [platform, setPlatform] = useState('leetcode')
  const [username, setUsername] = useState('')

  const handleTrial = (e: FormEvent) => {
    e.preventDefault()
    if (username.trim()) {
      router.push(`/dashboard?trial=${encodeURIComponent(username.trim())}&platform=${platform}`)
    }
  }

  return (
    <div className="min-h-screen bg-slate-950">
      <Navbar />
      <main className="mx-auto max-w-6xl px-4 py-16 sm:px-6 lg:px-8">
        <section className="card-lg bg-gradient-to-br from-slate-900/80 via-slate-900 to-slate-950/60 shadow-2xl shadow-emerald-500/10">
          <div className="space-y-4">
            <p className="section-label">Multi-Platform Competitive Programming AI</p>
            <h1 className="text-4xl font-semibold leading-tight text-white sm:text-5xl">
              Decode your coding journey with AI-powered clarity.
            </h1>
            <p className="text-lg text-slate-300">
              Connect your profiles across LeetCode, Codeforces, CodeChef, and HackerRank. Get unified analytics, AI insights, and a personal mentor.
            </p>
          </div>

          <div className="mt-8 flex flex-wrap gap-2">
            {PLATFORMS.map(p => (
              <PlatformBadge key={p.id} platform={p.id} username={p.label} />
            ))}
          </div>

          <form className="mt-6 flex flex-col gap-4 rounded-2xl border border-white/10 bg-white/5 p-4 sm:flex-row" onSubmit={handleTrial}>
            <select
              value={platform}
              onChange={(e) => setPlatform(e.target.value)}
              className="input-field sm:w-48"
            >
              {PLATFORMS.map(p => (
                <option key={p.id} value={p.id}>{p.label}</option>
              ))}
            </select>
            <div className="flex-1">
              <Input
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder={`Enter your ${PLATFORMS.find(p => p.id === platform)?.label} username`}
              />
            </div>
            <Button type="submit" className="self-end">
              Try Free Insights
            </Button>
          </form>

          <div className="mt-10 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <StatCard label="Platforms" value="4" subtext="LeetCode, Codeforces, CodeChef, HackerRank" />
            <StatCard label="AI Insights" value="Gemini" subtext="Powered by Google Gemini 2.0" />
            <StatCard label="Chat Mentor" value="24/7" subtext="Context-aware AI guidance" />
            <StatCard label="Recruitment" value="Smart" subtext="AI-matched job opportunities" />
          </div>
        </section>

        <section className="mt-16 grid gap-8 md:grid-cols-3">
          <FeatureCard
            title="Multi-Platform Aggregation"
            description="Connect all your competitive coding profiles. We scrape and unify your data across LeetCode, Codeforces, CodeChef, and HackerRank into one dashboard."
          />
          <FeatureCard
            title="AI-Powered Insights"
            description="Get personalized strengths, weaknesses, career recommendations, and a 90-day improvement roadmap — powered by cross-platform analysis."
          />
          <FeatureCard
            title="Smart Recruitment"
            description="Companies can create assessments, post jobs, and use AI to match candidates based on unified coding profiles and skills across all platforms."
          />
        </section>

        <section className="mt-16">
          <div className="text-center">
            <p className="section-label">Supported Platforms</p>
            <h2 className="mt-2 text-3xl font-semibold text-white">One dashboard for all your coding profiles</h2>
          </div>
          <div className="mt-8 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
            <PlatformCard
              name="LeetCode"
              description="Problems solved, difficulty breakdown, contest rating, topic stats, and submission heatmap"
              color="border-yellow-500/30 bg-yellow-500/5"
            />
            <PlatformCard
              name="Codeforces"
              description="Rating history, rank, contest performance, and per-tag problem analysis"
              color="border-blue-500/30 bg-blue-500/5"
            />
            <PlatformCard
              name="CodeChef"
              description="Star rating, problems by difficulty, contest history, and activity heatmap"
              color="border-orange-500/30 bg-orange-500/5"
            />
            <PlatformCard
              name="HackerRank"
              description="Track scores, badges, contest participation, and submission history"
              color="border-green-500/30 bg-green-500/5"
            />
          </div>
        </section>

        <section className="mt-16 text-center">
          <p className="section-label">Ready to level up?</p>
          <h2 className="mt-2 text-3xl font-semibold text-white">Create your free account</h2>
          <p className="mt-2 text-slate-400">Connect all your competitive programming profiles in one place</p>
          <div className="mt-6 flex justify-center gap-4">
            <Button onClick={() => router.push('/login')}>Sign In</Button>
            <Button variant="secondary" onClick={() => router.push('/register')}>
              Create Account
            </Button>
          </div>
        </section>
      </main>
      <Footer />
    </div>
  )
}

function FeatureCard({ title, description }: { title: string; description: string }) {
  return (
    <div className="card">
      <h3 className="text-xl font-semibold text-white">{title}</h3>
      <p className="mt-3 text-sm text-slate-300">{description}</p>
    </div>
  )
}

function PlatformCard({ name, description, color }: { name: string; description: string; color: string }) {
  return (
    <div className={`rounded-2xl border p-6 ${color}`}>
      <h3 className="text-lg font-semibold text-white">{name}</h3>
      <p className="mt-2 text-sm text-slate-400">{description}</p>
    </div>
  )
}

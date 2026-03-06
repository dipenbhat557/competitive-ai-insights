'use client'

import { useState } from 'react'
import { useProfile } from '@/lib/hooks/useProfile'
import Button from '@/components/ui/Button'
import Input from '@/components/ui/Input'
import Card from '@/components/ui/Card'
import PlatformBadge from '@/components/profile/PlatformBadge'

const PLATFORMS = ['leetcode', 'codeforces', 'codechef', 'hackerrank']

export default function SettingsPage() {
  const { profiles, linkProfile, unlinkProfile, isLoading } = useProfile()
  const [platform, setPlatform] = useState(PLATFORMS[0])
  const [username, setUsername] = useState('')

  const handleLink = async () => {
    if (!username.trim()) return
    await linkProfile(platform, username.trim())
    setUsername('')
  }

  return (
    <div className="space-y-8">
      <div>
        <p className="section-label">Settings</p>
        <h1 className="mt-1 text-3xl font-semibold text-white">Platform Connections</h1>
      </div>

      <Card>
        <h2 className="text-lg font-semibold text-white">Link a Platform</h2>
        <p className="mt-1 text-sm text-slate-400">Connect your LeetCode, Codeforces, CodeChef, or HackerRank profile to aggregate your data.</p>
        <div className="mt-4 flex flex-col gap-4 sm:flex-row">
          <select
            value={platform}
            onChange={e => setPlatform(e.target.value)}
            className="input-field sm:w-48"
          >
            {PLATFORMS.map(p => (
              <option key={p} value={p}>{p.charAt(0).toUpperCase() + p.slice(1)}</option>
            ))}
          </select>
          <Input
            value={username}
            onChange={e => setUsername(e.target.value)}
            placeholder="Platform username"
            className="flex-1"
          />
          <Button onClick={handleLink} disabled={isLoading}>
            {isLoading ? 'Linking...' : 'Link'}
          </Button>
        </div>
      </Card>

      <Card>
        <h2 className="text-lg font-semibold text-white">Connected Platforms</h2>
        {profiles.length === 0 ? (
          <p className="mt-4 text-sm text-slate-400">No platforms connected yet.</p>
        ) : (
          <div className="mt-4 space-y-3">
            {profiles.map(p => (
              <div key={p.id} className="flex items-center justify-between rounded-xl border border-white/10 bg-slate-950/60 p-4">
                <PlatformBadge platform={p.platform} username={p.platform_username} />
                <Button variant="secondary" onClick={() => unlinkProfile(p.id)} className="text-sm">
                  Unlink
                </Button>
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  )
}

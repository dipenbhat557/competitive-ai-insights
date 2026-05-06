'use client'

import { useEffect, useState } from 'react'
import Card from '@/components/ui/Card'
import { apiClient } from '@/lib/api-client'
import type { Job } from '@/lib/types'

interface Application {
  id: string
  job_id: string
  user_id: string
  status: string
  ai_match_score: number | null
  ai_match_reason: string | null
  created_at: string
}

export default function CandidatesPage() {
  const [jobs, setJobs] = useState<Job[]>([])
  const [selectedJobId, setSelectedJobId] = useState<string | null>(null)
  const [apps, setApps] = useState<Application[] | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    apiClient<Job[]>('/api/v1/jobs?is_active=true')
      .then(data => {
        setJobs(data)
        if (data.length > 0) setSelectedJobId(data[0].id)
      })
      .catch(e => setError(e instanceof Error ? e.message : 'Failed to load jobs'))
      .finally(() => setLoading(false))
  }, [])

  useEffect(() => {
    if (!selectedJobId) return
    setApps(null)
    apiClient<Application[]>(`/api/v1/jobs/${selectedJobId}/applicants`)
      .then(setApps)
      .catch(e => setError(e instanceof Error ? e.message : 'Failed to load applicants'))
  }, [selectedJobId])

  return (
    <div className="space-y-8">
      <div>
        <p className="section-label">Candidates</p>
        <h1 className="mt-1 text-3xl font-semibold text-white">Candidate Browser</h1>
        <p className="mt-1 text-sm text-slate-400">
          Pick a job to see applicants ranked by AI fit score.
        </p>
      </div>

      {error && (
        <div className="rounded-lg border border-red-500/20 bg-red-500/10 p-3 text-sm text-red-400">
          {error}
        </div>
      )}

      {loading ? (
        <Card className="py-12 text-center">
          <p className="text-slate-400">Loading...</p>
        </Card>
      ) : jobs.length === 0 ? (
        <Card className="py-12 text-center">
          <p className="text-slate-400">Post a job first to see applicants here.</p>
        </Card>
      ) : (
        <>
          <Card>
            <label className="section-label">Job</label>
            <select
              className="input-field mt-1"
              value={selectedJobId ?? ''}
              onChange={e => setSelectedJobId(e.target.value)}
            >
              {jobs.map(j => (
                <option key={j.id} value={j.id}>
                  {j.title}
                </option>
              ))}
            </select>
          </Card>

          {apps === null ? (
            <Card className="py-12 text-center">
              <p className="text-slate-400">Loading applicants...</p>
            </Card>
          ) : apps.length === 0 ? (
            <Card className="py-12 text-center">
              <p className="text-slate-400">No applicants for this job yet.</p>
            </Card>
          ) : (
            <div className="space-y-3">
              {apps
                .slice()
                .sort((a, b) => (b.ai_match_score ?? 0) - (a.ai_match_score ?? 0))
                .map(app => (
                  <Card key={app.id}>
                    <div className="flex items-start justify-between gap-4">
                      <div className="min-w-0 flex-1">
                        <p className="font-mono text-xs text-slate-400">{app.user_id}</p>
                        <p className="mt-2 text-sm text-slate-300">
                          Status · <span className="text-white">{app.status}</span>
                        </p>
                        {app.ai_match_reason && (
                          <p className="mt-2 text-sm text-slate-300">{app.ai_match_reason}</p>
                        )}
                      </div>
                      {app.ai_match_score != null && (
                        <div className="text-right">
                          <div className="text-2xl font-semibold text-emerald-300">
                            {Math.round(app.ai_match_score)}
                          </div>
                          <div className="text-[11px] uppercase tracking-wide text-slate-500">
                            Fit
                          </div>
                        </div>
                      )}
                    </div>
                  </Card>
                ))}
            </div>
          )}
        </>
      )}
    </div>
  )
}

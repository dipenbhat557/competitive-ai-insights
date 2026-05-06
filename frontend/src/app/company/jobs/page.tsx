'use client'

import { useEffect, useState } from 'react'
import Card from '@/components/ui/Card'
import Button from '@/components/ui/Button'
import { apiClient } from '@/lib/api-client'
import type { Job } from '@/lib/types'

export default function JobsPage() {
  const [jobs, setJobs] = useState<Job[] | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [showForm, setShowForm] = useState(false)

  const refresh = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await apiClient<Job[]>('/api/v1/jobs?is_active=true')
      setJobs(data)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load jobs')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    refresh()
  }, [])

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <p className="section-label">Jobs</p>
          <h1 className="mt-1 text-3xl font-semibold text-white">Job Postings</h1>
        </div>
        <Button onClick={() => setShowForm(s => !s)}>
          {showForm ? 'Cancel' : 'Post a Job'}
        </Button>
      </div>

      {error && (
        <div className="rounded-lg border border-red-500/20 bg-red-500/10 p-3 text-sm text-red-400">
          {error}
        </div>
      )}

      {showForm && (
        <PostJobForm
          onCreated={() => {
            setShowForm(false)
            refresh()
          }}
        />
      )}

      {loading ? (
        <Card className="py-12 text-center">
          <p className="text-slate-400">Loading...</p>
        </Card>
      ) : jobs && jobs.length === 0 ? (
        <Card className="py-12 text-center">
          <p className="text-slate-400">No jobs posted yet.</p>
        </Card>
      ) : (
        <div className="space-y-3">
          {jobs?.map(job => (
            <Card key={job.id}>
              <div className="flex items-start justify-between gap-4">
                <div className="min-w-0 flex-1">
                  <h3 className="font-semibold text-white">{job.title}</h3>
                  <p className="mt-1 line-clamp-2 text-sm text-slate-400">{job.description}</p>
                  {job.required_skills.length > 0 && (
                    <div className="mt-2 flex flex-wrap gap-1.5">
                      {job.required_skills.slice(0, 8).map((s, i) => (
                        <span
                          key={i}
                          className="rounded-full border border-white/10 bg-white/5 px-2 py-0.5 text-xs text-slate-300"
                        >
                          {s}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
                <div className="text-right text-xs text-slate-500">
                  {job.is_active ? 'Active' : 'Inactive'}
                  {job.min_overall_score != null && (
                    <div className="mt-1">Min score {job.min_overall_score}</div>
                  )}
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}

function PostJobForm({ onCreated }: { onCreated: () => void }) {
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [skills, setSkills] = useState('')
  const [minScore, setMinScore] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSubmitting(true)
    setError(null)
    try {
      await apiClient('/api/v1/jobs', {
        method: 'POST',
        body: JSON.stringify({
          title,
          description,
          required_skills: skills
            .split(',')
            .map(s => s.trim())
            .filter(Boolean),
          min_overall_score: minScore ? Number(minScore) : null,
          is_active: true,
        }),
      })
      onCreated()
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to create job')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <Card>
      <form onSubmit={submit} className="space-y-4">
        <div>
          <label className="section-label">Title</label>
          <input
            className="input-field mt-1"
            value={title}
            onChange={e => setTitle(e.target.value)}
            required
          />
        </div>
        <div>
          <label className="section-label">Description</label>
          <textarea
            className="input-field mt-1 min-h-[120px]"
            value={description}
            onChange={e => setDescription(e.target.value)}
            required
          />
        </div>
        <div className="grid gap-4 sm:grid-cols-2">
          <div>
            <label className="section-label">Required skills (comma-separated)</label>
            <input
              className="input-field mt-1"
              value={skills}
              onChange={e => setSkills(e.target.value)}
              placeholder="python, kubernetes, system design"
            />
          </div>
          <div>
            <label className="section-label">Min overall score (optional)</label>
            <input
              type="number"
              className="input-field mt-1"
              value={minScore}
              onChange={e => setMinScore(e.target.value)}
              min={0}
              max={100}
            />
          </div>
        </div>
        {error && <p className="text-sm text-red-400">{error}</p>}
        <Button type="submit" disabled={submitting}>
          {submitting ? 'Posting...' : 'Post Job'}
        </Button>
      </form>
    </Card>
  )
}

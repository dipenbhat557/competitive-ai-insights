'use client'

import { useState } from 'react'
import Card from '@/components/ui/Card'
import Button from '@/components/ui/Button'
import { apiClient } from '@/lib/api-client'
import type { Assessment } from '@/lib/types'

export default function AssessmentsPage() {
  const [created, setCreated] = useState<Assessment[]>([])
  const [showForm, setShowForm] = useState(false)
  const [error, setError] = useState<string | null>(null)

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <p className="section-label">Assessments</p>
          <h1 className="mt-1 text-3xl font-semibold text-white">Coding Assessments</h1>
        </div>
        <Button onClick={() => setShowForm(s => !s)}>
          {showForm ? 'Cancel' : 'Create Assessment'}
        </Button>
      </div>

      {error && (
        <div className="rounded-lg border border-red-500/20 bg-red-500/10 p-3 text-sm text-red-400">
          {error}
        </div>
      )}

      {showForm && (
        <CreateAssessmentForm
          onCreated={a => {
            setCreated(c => [a, ...c])
            setShowForm(false)
          }}
          onError={setError}
        />
      )}

      {created.length === 0 ? (
        <Card className="py-12 text-center">
          <p className="text-slate-400">No assessments created yet.</p>
        </Card>
      ) : (
        <div className="space-y-3">
          {created.map(a => (
            <Card key={a.id}>
              <h3 className="font-semibold text-white">{a.title}</h3>
              <p className="mt-1 text-sm text-slate-400">{a.description}</p>
              <p className="mt-2 text-xs text-slate-500">Time limit · {a.time_limit_mins} min</p>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}

function CreateAssessmentForm({
  onCreated,
  onError,
}: {
  onCreated: (a: Assessment) => void
  onError: (msg: string) => void
}) {
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [timeLimit, setTimeLimit] = useState('60')
  const [submitting, setSubmitting] = useState(false)

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSubmitting(true)
    onError('')
    try {
      const a = await apiClient<Assessment>('/api/v1/assessments', {
        method: 'POST',
        body: JSON.stringify({
          title,
          description,
          time_limit_mins: Number(timeLimit) || 60,
        }),
      })
      onCreated(a)
      setTitle('')
      setDescription('')
    } catch (e) {
      onError(e instanceof Error ? e.message : 'Failed to create assessment')
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
            className="input-field mt-1 min-h-[100px]"
            value={description}
            onChange={e => setDescription(e.target.value)}
            required
          />
        </div>
        <div>
          <label className="section-label">Time limit (minutes)</label>
          <input
            type="number"
            className="input-field mt-1 w-32"
            value={timeLimit}
            onChange={e => setTimeLimit(e.target.value)}
            min={5}
            max={300}
          />
        </div>
        <Button type="submit" disabled={submitting}>
          {submitting ? 'Creating...' : 'Create Assessment'}
        </Button>
      </form>
    </Card>
  )
}

'use client'

import Card from '@/components/ui/Card'
import Button from '@/components/ui/Button'
import { useRouter } from 'next/navigation'

export default function CompanyPage() {
  const router = useRouter()

  return (
    <div className="space-y-8">
      <div>
        <p className="section-label">Company</p>
        <h1 className="mt-1 text-3xl font-semibold text-white">Recruitment Dashboard</h1>
      </div>

      <div className="grid gap-4 sm:grid-cols-3">
        <Card className="cursor-pointer transition hover:border-emerald-500/30" onClick={() => router.push('/company/assessments')}>
          <h3 className="text-lg font-semibold text-white">Assessments</h3>
          <p className="mt-2 text-sm text-slate-400">Create and manage coding assessments</p>
        </Card>
        <Card className="cursor-pointer transition hover:border-emerald-500/30" onClick={() => router.push('/company/jobs')}>
          <h3 className="text-lg font-semibold text-white">Job Postings</h3>
          <p className="mt-2 text-sm text-slate-400">Post jobs and review applications</p>
        </Card>
        <Card className="cursor-pointer transition hover:border-emerald-500/30" onClick={() => router.push('/company/candidates')}>
          <h3 className="text-lg font-semibold text-white">Candidates</h3>
          <p className="mt-2 text-sm text-slate-400">Browse and evaluate candidates</p>
        </Card>
      </div>
    </div>
  )
}

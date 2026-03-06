'use client'

import Card from '@/components/ui/Card'
import Button from '@/components/ui/Button'

export default function JobsPage() {
  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <p className="section-label">Jobs</p>
          <h1 className="mt-1 text-3xl font-semibold text-white">Job Postings</h1>
        </div>
        <Button>Post a Job</Button>
      </div>
      <Card className="py-12 text-center">
        <p className="text-slate-400">No jobs posted yet.</p>
      </Card>
    </div>
  )
}

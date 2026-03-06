'use client'

import Card from '@/components/ui/Card'
import Button from '@/components/ui/Button'

export default function AssessmentsPage() {
  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <p className="section-label">Assessments</p>
          <h1 className="mt-1 text-3xl font-semibold text-white">Coding Assessments</h1>
        </div>
        <Button>Create Assessment</Button>
      </div>
      <Card className="py-12 text-center">
        <p className="text-slate-400">No assessments created yet.</p>
      </Card>
    </div>
  )
}

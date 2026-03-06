'use client'

import Card from '@/components/ui/Card'

export default function CandidatesPage() {
  return (
    <div className="space-y-8">
      <div>
        <p className="section-label">Candidates</p>
        <h1 className="mt-1 text-3xl font-semibold text-white">Candidate Browser</h1>
      </div>
      <Card className="py-12 text-center">
        <p className="text-slate-400">Search and filter candidates by skills and scores.</p>
      </Card>
    </div>
  )
}

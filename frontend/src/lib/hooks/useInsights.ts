'use client'

import { useState, useEffect, useCallback } from 'react'
import { apiClient } from '@/lib/api-client'
import type { InsightReport } from '@/lib/types'

export function useInsights() {
  const [insights, setInsights] = useState<InsightReport | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchInsights = useCallback(async () => {
    try {
      const data = await apiClient<InsightReport>('/api/v1/insights/latest')
      setInsights(data)
    } catch {
      // No insights yet
    }
  }, [])

  useEffect(() => {
    fetchInsights()
  }, [fetchInsights])

  const generate = async () => {
    setIsLoading(true)
    setError(null)
    try {
      const data = await apiClient<InsightReport>('/api/v1/insights/generate?force=true', { method: 'POST' })
      setInsights(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate insights')
    } finally {
      setIsLoading(false)
    }
  }

  return { insights, isLoading, error, generate }
}

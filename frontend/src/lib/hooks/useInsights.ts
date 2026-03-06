'use client'

import { useState, useEffect, useCallback } from 'react'
import { apiClient } from '@/lib/api-client'
import type { InsightReport } from '@/lib/types'

export function useInsights() {
  const [insights, setInsights] = useState<InsightReport | null>(null)
  const [isLoading, setIsLoading] = useState(false)

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
    try {
      const data = await apiClient<InsightReport>('/api/v1/insights/generate', { method: 'POST' })
      setInsights(data)
    } finally {
      setIsLoading(false)
    }
  }

  return { insights, isLoading, generate }
}

'use client'

import { useState, useEffect, useCallback } from 'react'
import { apiClient } from '@/lib/api-client'
import type { CodingProfile, NormalizedAggregate, PlatformSnapshot } from '@/lib/types'

export function useProfile() {
  const [profiles, setProfiles] = useState<CodingProfile[]>([])
  const [latestSnapshots, setLatestSnapshots] = useState<PlatformSnapshot[]>([])
  const [normalized, setNormalized] = useState<NormalizedAggregate | null>(null)
  const [isLoading, setIsLoading] = useState(false)

  const fetchProfiles = useCallback(async () => {
    try {
      const data = await apiClient<{
        profiles: CodingProfile[]
        snapshots: PlatformSnapshot[]
        normalized: NormalizedAggregate | null
      }>('/api/v1/profiles')
      setProfiles(data.profiles)
      setLatestSnapshots(data.snapshots)
      setNormalized(data.normalized)
    } catch {
      // Not logged in or no profiles
    }
  }, [])

  useEffect(() => {
    fetchProfiles()
  }, [fetchProfiles])

  const linkProfile = async (platform: string, username: string) => {
    setIsLoading(true)
    try {
      await apiClient('/api/v1/profiles/link', {
        method: 'POST',
        body: JSON.stringify({ platform, platform_username: username }),
      })
      await fetchProfiles()
    } finally {
      setIsLoading(false)
    }
  }

  const unlinkProfile = async (profileId: string) => {
    setIsLoading(true)
    try {
      await apiClient(`/api/v1/profiles/${profileId}`, { method: 'DELETE' })
      await fetchProfiles()
    } finally {
      setIsLoading(false)
    }
  }

  const scrapeAll = async () => {
    setIsLoading(true)
    try {
      await apiClient('/api/v1/profiles/scrape', { method: 'POST' })
      await fetchProfiles()
    } finally {
      setIsLoading(false)
    }
  }

  return { profiles, latestSnapshots, normalized, isLoading, linkProfile, unlinkProfile, scrapeAll, fetchProfiles }
}

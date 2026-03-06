'use client'

import { useEffect } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { useAuth } from '@/lib/hooks/useAuth'
import { Suspense } from 'react'

function OAuthCallbackInner() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const { handleOAuthCallback } = useAuth()

  useEffect(() => {
    const token = searchParams.get('token')
    const refreshToken = searchParams.get('refresh_token')
    if (token && refreshToken) {
      handleOAuthCallback(token, refreshToken)
      router.push('/dashboard')
    } else {
      router.push('/login?error=oauth_failed')
    }
  }, [searchParams, router, handleOAuthCallback])

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-950">
      <p className="text-slate-400">Completing sign in...</p>
    </div>
  )
}

export default function OAuthCallbackPage() {
  return (
    <Suspense fallback={<div className="flex min-h-screen items-center justify-center bg-slate-950"><p className="text-slate-400">Loading...</p></div>}>
      <OAuthCallbackInner />
    </Suspense>
  )
}

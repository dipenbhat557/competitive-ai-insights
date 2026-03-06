'use client'

import Link from 'next/link'
import Image from 'next/image'
import { useAuth } from '@/lib/hooks/useAuth'
import Button from '@/components/ui/Button'

export default function Navbar() {
  const { user, logout } = useAuth()

  return (
    <nav className="border-b border-white/10 bg-slate-950/80 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4 sm:px-6 lg:px-8">
        <Link href="/" className="flex items-center gap-2 text-xl font-semibold text-white">
          <Image src="/logo.png" alt="CodePulse AI" width={32} height={32} className="rounded-lg" />
          <span><span className="text-emerald-400">Code</span>Pulse AI</span>
        </Link>
        <div className="flex items-center gap-4">
          {user ? (
            <>
              <Link href="/dashboard" className="text-sm text-slate-300 hover:text-white">Dashboard</Link>
              <button onClick={logout} className="text-sm text-slate-400 hover:text-white">Sign Out</button>
            </>
          ) : (
            <>
              <Link href="/login"><Button variant="secondary" className="text-sm">Sign In</Button></Link>
              <Link href="/register"><Button className="text-sm">Get Started</Button></Link>
            </>
          )}
        </div>
      </div>
    </nav>
  )
}

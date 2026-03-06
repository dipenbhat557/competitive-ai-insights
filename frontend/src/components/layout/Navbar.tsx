'use client'

import { useState, useRef, useEffect } from 'react'
import Link from 'next/link'
import Image from 'next/image'
import { useAuth } from '@/lib/hooks/useAuth'
import Button from '@/components/ui/Button'

export default function Navbar() {
  const { user, logout } = useAuth()
  const [menuOpen, setMenuOpen] = useState(false)
  const [mobileNav, setMobileNav] = useState(false)
  const menuRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setMenuOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  return (
    <nav className="border-b border-white/10 bg-slate-950/80 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3 sm:py-4 sm:px-6 lg:px-8">
        <Link href="/" className="flex items-center gap-2 text-lg font-semibold text-white sm:text-xl">
          <Image src="/logo.png" alt="CodePulse AI" width={28} height={28} className="rounded-lg sm:h-8 sm:w-8" />
          <span><span className="text-emerald-400">Code</span>Pulse AI</span>
        </Link>

        {/* Desktop nav */}
        <div className="hidden items-center gap-4 sm:flex">
          {user ? (
            <>
              <Link href="/dashboard" className="text-sm text-slate-300 hover:text-white">Dashboard</Link>
              <div className="relative" ref={menuRef}>
                <button
                  onClick={() => setMenuOpen(!menuOpen)}
                  className="flex items-center gap-2 rounded-full focus:outline-none focus:ring-2 focus:ring-emerald-400/50"
                >
                  {user.avatar_url ? (
                    <img
                      src={user.avatar_url}
                      alt={user.full_name}
                      className="h-8 w-8 rounded-full object-cover"
                    />
                  ) : (
                    <div className="flex h-8 w-8 items-center justify-center rounded-full bg-emerald-500/20 text-sm font-medium text-emerald-400">
                      {user.full_name?.charAt(0)?.toUpperCase() || user.email.charAt(0).toUpperCase()}
                    </div>
                  )}
                </button>
                {menuOpen && (
                  <div className="absolute right-0 z-50 mt-2 w-48 rounded-lg border border-white/10 bg-slate-900 py-1 shadow-xl">
                    <div className="border-b border-white/10 px-4 py-2">
                      <p className="truncate text-sm font-medium text-white">{user.full_name}</p>
                      <p className="truncate text-xs text-slate-400">{user.email}</p>
                    </div>
                    <Link
                      href="/dashboard/settings"
                      onClick={() => setMenuOpen(false)}
                      className="block px-4 py-2 text-sm text-slate-300 hover:bg-white/5 hover:text-white"
                    >
                      Settings
                    </Link>
                    <button
                      onClick={() => { setMenuOpen(false); logout() }}
                      className="w-full px-4 py-2 text-left text-sm text-red-400 hover:bg-white/5 hover:text-red-300"
                    >
                      Sign Out
                    </button>
                  </div>
                )}
              </div>
            </>
          ) : (
            <>
              <Link href="/login"><Button variant="secondary" className="text-sm">Sign In</Button></Link>
              <Link href="/register"><Button className="text-sm">Get Started</Button></Link>
            </>
          )}
        </div>

        {/* Mobile: avatar/hamburger */}
        <div className="flex items-center gap-3 sm:hidden">
          {user ? (
            <button
              onClick={() => setMobileNav(!mobileNav)}
              className="flex items-center rounded-full focus:outline-none"
            >
              {user.avatar_url ? (
                <img src={user.avatar_url} alt={user.full_name} className="h-8 w-8 rounded-full object-cover" />
              ) : (
                <div className="flex h-8 w-8 items-center justify-center rounded-full bg-emerald-500/20 text-sm font-medium text-emerald-400">
                  {user.full_name?.charAt(0)?.toUpperCase() || user.email.charAt(0).toUpperCase()}
                </div>
              )}
            </button>
          ) : (
            <button onClick={() => setMobileNav(!mobileNav)} className="text-slate-300">
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                {mobileNav ? (
                  <path strokeLinecap="round" strokeLinejoin="round" d="M6 18 18 6M6 6l12 12" />
                ) : (
                  <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5" />
                )}
              </svg>
            </button>
          )}
        </div>
      </div>

      {/* Mobile dropdown */}
      {mobileNav && (
        <div className="border-t border-white/10 px-4 pb-4 pt-2 sm:hidden">
          {user ? (
            <div className="space-y-1">
              <div className="border-b border-white/10 pb-2 mb-2">
                <p className="truncate text-sm font-medium text-white">{user.full_name}</p>
                <p className="truncate text-xs text-slate-400">{user.email}</p>
              </div>
              <Link href="/dashboard" onClick={() => setMobileNav(false)} className="block rounded-lg px-3 py-2 text-sm text-slate-300 hover:bg-white/5">Dashboard</Link>
              <Link href="/dashboard/insights" onClick={() => setMobileNav(false)} className="block rounded-lg px-3 py-2 text-sm text-slate-300 hover:bg-white/5">AI Insights</Link>
              <Link href="/dashboard/chat" onClick={() => setMobileNav(false)} className="block rounded-lg px-3 py-2 text-sm text-slate-300 hover:bg-white/5">AI Mentor</Link>
              <Link href="/dashboard/settings" onClick={() => setMobileNav(false)} className="block rounded-lg px-3 py-2 text-sm text-slate-300 hover:bg-white/5">Settings</Link>
              <button
                onClick={() => { setMobileNav(false); logout() }}
                className="w-full rounded-lg px-3 py-2 text-left text-sm text-red-400 hover:bg-white/5"
              >
                Sign Out
              </button>
            </div>
          ) : (
            <div className="flex flex-col gap-2">
              <Link href="/login" onClick={() => setMobileNav(false)}><Button variant="secondary" className="w-full text-sm">Sign In</Button></Link>
              <Link href="/register" onClick={() => setMobileNav(false)}><Button className="w-full text-sm">Get Started</Button></Link>
            </div>
          )}
        </div>
      )}
    </nav>
  )
}

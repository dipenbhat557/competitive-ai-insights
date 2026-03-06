'use client'

import { useState } from 'react'
import { useChat } from '@/lib/hooks/useChat'
import ChatWindow from '@/components/chat/ChatWindow'
import Button from '@/components/ui/Button'
import Card from '@/components/ui/Card'

export default function ChatPage() {
  const { sessions, activeSession, messages, isLoading, createSession, selectSession, sendMessage } = useChat()
  const [showSessions, setShowSessions] = useState(false)

  return (
    <div className="space-y-4 sm:space-y-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p className="section-label">AI Mentor</p>
          <h1 className="mt-1 text-2xl font-semibold text-white sm:text-3xl">Chat with Your Mentor</h1>
        </div>
        <div className="flex gap-2">
          <Button variant="secondary" onClick={() => setShowSessions(!showSessions)} className="text-sm lg:hidden">
            {showSessions ? 'Hide Sessions' : 'Sessions'}
          </Button>
          <Button onClick={() => createSession()} className="text-sm">New Chat</Button>
        </div>
      </div>

      <div className="flex gap-6">
        {/* Sessions panel — always visible on lg, toggle on mobile */}
        <div className={`${showSessions ? 'block' : 'hidden'} w-full shrink-0 space-y-3 sm:w-64 lg:block`}>
          <div className="space-y-2">
            {sessions.length === 0 ? (
              <p className="text-sm text-slate-500">No sessions yet. Start a new chat.</p>
            ) : (
              sessions.map(s => (
                <button
                  key={s.id}
                  onClick={() => { selectSession(s.id); setShowSessions(false) }}
                  className={`w-full rounded-xl border p-3 text-left text-sm transition ${
                    activeSession === s.id
                      ? 'border-emerald-500/30 bg-emerald-500/10 text-white'
                      : 'border-white/10 bg-slate-900/50 text-slate-400 hover:text-white'
                  }`}
                >
                  {s.title || 'Untitled Chat'}
                  <p className="mt-1 text-xs text-slate-500">{new Date(s.created_at).toLocaleDateString()}</p>
                </button>
              ))
            )}
          </div>
        </div>

        {/* Chat area — hide when sessions panel is open on mobile */}
        <div className={`min-w-0 flex-1 ${showSessions ? 'hidden sm:block' : 'block'}`}>
          {activeSession ? (
            <ChatWindow messages={messages} onSend={sendMessage} isLoading={isLoading} />
          ) : (
            <Card className="py-12 text-center">
              <p className="text-lg font-semibold text-white">Start a conversation</p>
              <p className="mt-2 text-sm text-slate-400">Create a new chat to talk with your AI mentor.</p>
            </Card>
          )}
        </div>
      </div>
    </div>
  )
}

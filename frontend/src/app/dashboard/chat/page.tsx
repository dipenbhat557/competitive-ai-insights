'use client'

import { useState } from 'react'
import { useChat } from '@/lib/hooks/useChat'
import ChatWindow from '@/components/chat/ChatWindow'
import Button from '@/components/ui/Button'
import Card from '@/components/ui/Card'

export default function ChatPage() {
  const { sessions, activeSession, messages, isLoading, createSession, selectSession, sendMessage } = useChat()
  const [showSessions, setShowSessions] = useState(true)

  return (
    <div className="space-y-6">
      <div>
        <p className="section-label">AI Mentor</p>
        <h1 className="mt-1 text-3xl font-semibold text-white">Chat with Your Mentor</h1>
      </div>

      <div className="flex gap-6">
        {showSessions && (
          <div className="w-64 shrink-0 space-y-3">
            <Button onClick={() => createSession()} className="w-full">New Chat</Button>
            <div className="space-y-2">
              {sessions.map(s => (
                <button
                  key={s.id}
                  onClick={() => selectSession(s.id)}
                  className={`w-full rounded-xl border p-3 text-left text-sm transition ${
                    activeSession === s.id
                      ? 'border-emerald-500/30 bg-emerald-500/10 text-white'
                      : 'border-white/10 bg-slate-900/50 text-slate-400 hover:text-white'
                  }`}
                >
                  {s.title || 'Untitled Chat'}
                  <p className="mt-1 text-xs text-slate-500">{new Date(s.created_at).toLocaleDateString()}</p>
                </button>
              ))}
            </div>
          </div>
        )}

        <div className="flex-1">
          <button onClick={() => setShowSessions(!showSessions)} className="mb-3 text-xs text-slate-500 hover:text-slate-300 lg:hidden">
            {showSessions ? 'Hide sessions' : 'Show sessions'}
          </button>
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

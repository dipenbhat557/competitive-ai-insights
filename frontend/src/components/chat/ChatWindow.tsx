'use client'

import { useRef, useEffect } from 'react'
import ChatMessage from './ChatMessage'
import ChatInput from './ChatInput'
import type { ChatMessageType } from '@/lib/types'

interface Props {
  messages: ChatMessageType[]
  onSend: (content: string) => void
  isLoading: boolean
}

export default function ChatWindow({ messages, onSend, isLoading }: Props) {
  const scrollRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' })
  }, [messages])

  return (
    <div className="card flex h-[calc(100vh-16rem)] min-h-[400px] max-h-[600px] flex-col p-0 sm:max-h-none sm:h-[600px]">
      <div className="border-b border-white/10 px-6 py-4">
        <p className="section-label">AI Copilot</p>
        <h3 className="mt-1 text-lg font-semibold text-white">Chat with your mentor</h3>
      </div>
      <div ref={scrollRef} className="flex-1 overflow-auto px-6 py-4">
        <div className="space-y-4">
          {messages.map(msg => (
            <ChatMessage key={msg.id} message={msg} />
          ))}
          {isLoading && (
            <div className="flex gap-1">
              <div className="h-2 w-2 animate-bounce rounded-full bg-emerald-400" />
              <div className="h-2 w-2 animate-bounce rounded-full bg-emerald-400" style={{ animationDelay: '0.1s' }} />
              <div className="h-2 w-2 animate-bounce rounded-full bg-emerald-400" style={{ animationDelay: '0.2s' }} />
            </div>
          )}
        </div>
      </div>
      <ChatInput onSend={onSend} disabled={isLoading} />
    </div>
  )
}

'use client'

import ReactMarkdown from 'react-markdown'
import type { ChatMessageType } from '@/lib/types'

export default function ChatMessage({ message }: { message: ChatMessageType }) {
  const isUser = message.role === 'user'
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className={`max-w-[85%] rounded-2xl px-4 py-3 sm:max-w-[80%] ${
        isUser
          ? 'bg-emerald-500/20 text-emerald-100'
          : 'bg-slate-800 text-slate-200'
      }`}>
        {isUser ? (
          <p className="text-sm whitespace-pre-wrap">{message.content}</p>
        ) : (
          <div className="prose-chat text-sm">
            <ReactMarkdown>{message.content}</ReactMarkdown>
          </div>
        )}
      </div>
    </div>
  )
}

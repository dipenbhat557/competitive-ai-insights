import type { ChatMessageType } from '@/lib/types'

export default function ChatMessage({ message }: { message: ChatMessageType }) {
  const isUser = message.role === 'user'
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className={`max-w-[80%] rounded-2xl px-4 py-3 ${
        isUser
          ? 'bg-emerald-500/20 text-emerald-100'
          : 'bg-slate-800 text-slate-200'
      }`}>
        <p className="text-sm">{message.content}</p>
      </div>
    </div>
  )
}

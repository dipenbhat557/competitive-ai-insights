'use client'

import { useState, FormEvent } from 'react'
import Button from '@/components/ui/Button'

interface Props {
  onSend: (content: string) => void
  disabled?: boolean
}

export default function ChatInput({ onSend, disabled }: Props) {
  const [value, setValue] = useState('')

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault()
    if (!value.trim() || disabled) return
    onSend(value.trim())
    setValue('')
  }

  return (
    <form onSubmit={handleSubmit} className="flex gap-3 border-t border-white/10 p-4">
      <input
        value={value}
        onChange={e => setValue(e.target.value)}
        placeholder="Ask about practice schedules, contests, or interviews..."
        className="input-field flex-1"
        disabled={disabled}
      />
      <Button type="submit" disabled={disabled || !value.trim()}>Send</Button>
    </form>
  )
}

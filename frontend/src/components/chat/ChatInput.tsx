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
    <form onSubmit={handleSubmit} className="flex gap-2 border-t border-white/10 p-3 sm:gap-3 sm:p-4">
      <input
        value={value}
        onChange={e => setValue(e.target.value)}
        placeholder="Ask your mentor..."
        className="input-field flex-1 !px-3 !py-2 text-sm sm:!px-4 sm:!py-3 sm:text-base"
        disabled={disabled}
      />
      <Button type="submit" disabled={disabled || !value.trim()} className="!px-4 !py-2 text-sm sm:!px-6 sm:!py-3">Send</Button>
    </form>
  )
}

'use client'

import { useState, useEffect, useCallback } from 'react'
import { apiClient } from '@/lib/api-client'
import type { ChatSession, ChatMessageType } from '@/lib/types'

export function useChat() {
  const [sessions, setSessions] = useState<ChatSession[]>([])
  const [activeSession, setActiveSession] = useState<string | null>(null)
  const [messages, setMessages] = useState<ChatMessageType[]>([])
  const [isLoading, setIsLoading] = useState(false)

  const fetchSessions = useCallback(async () => {
    try {
      const data = await apiClient<ChatSession[]>('/api/v1/chat/sessions')
      setSessions(data)
    } catch {
      // Not logged in
    }
  }, [])

  useEffect(() => {
    fetchSessions()
  }, [fetchSessions])

  const createSession = async () => {
    const data = await apiClient<ChatSession>('/api/v1/chat/sessions', {
      method: 'POST',
      body: JSON.stringify({ title: 'New Chat' }),
    })
    setSessions(prev => [data, ...prev])
    setActiveSession(data.id)
    setMessages([])
  }

  const selectSession = async (id: string) => {
    setActiveSession(id)
    const data = await apiClient<{ messages: ChatMessageType[] }>(`/api/v1/chat/sessions/${id}`)
    setMessages(data.messages)
  }

  const sendMessage = async (content: string) => {
    if (!activeSession) return
    setIsLoading(true)
    const userMsg: ChatMessageType = {
      id: `temp-${Date.now()}`,
      role: 'user',
      content,
      created_at: new Date().toISOString(),
    }
    setMessages(prev => [...prev, userMsg])
    try {
      const data = await apiClient<{ user_message: ChatMessageType; assistant_message: ChatMessageType }>(
        `/api/v1/chat/sessions/${activeSession}/messages`,
        { method: 'POST', body: JSON.stringify({ content }) }
      )
      setMessages(prev => [...prev.filter(m => m.id !== userMsg.id), data.user_message, data.assistant_message])
      // Refresh sessions to pick up AI-generated title
      fetchSessions()
    } catch {
      setMessages(prev => prev.filter(m => m.id !== userMsg.id))
    } finally {
      setIsLoading(false)
    }
  }

  return { sessions, activeSession, messages, isLoading, createSession, selectSession, sendMessage }
}

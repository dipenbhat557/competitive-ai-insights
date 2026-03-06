'use client'

import { useEffect, useRef } from 'react'

interface ModalProps {
  open: boolean
  onClose: () => void
  children: React.ReactNode
  title?: string
}

export default function Modal({ open, onClose, children, title }: ModalProps) {
  const ref = useRef<HTMLDialogElement>(null)

  useEffect(() => {
    if (open) ref.current?.showModal()
    else ref.current?.close()
  }, [open])

  return (
    <dialog
      ref={ref}
      onClose={onClose}
      className="w-full max-w-lg rounded-2xl border border-white/10 bg-slate-900 p-6 text-white backdrop:bg-black/60"
    >
      {title && <h2 className="text-xl font-semibold">{title}</h2>}
      <div className="mt-4">{children}</div>
    </dialog>
  )
}

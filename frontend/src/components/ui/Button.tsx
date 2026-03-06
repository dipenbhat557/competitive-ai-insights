import { ButtonHTMLAttributes } from 'react'

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary'
}

export default function Button({ variant = 'primary', className = '', children, ...props }: ButtonProps) {
  const base = variant === 'primary' ? 'btn-primary' : 'btn-secondary'
  return (
    <button className={`${base} ${className}`} {...props}>
      {children}
    </button>
  )
}

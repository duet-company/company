'use client'

import React from 'react'

interface BadgeProps {
  children: React.ReactNode
  variant?: 'default' | 'accent' | 'success' | 'error'
  size?: 'sm' | 'md' | 'lg'
  className?: string
}

export function Badge({ children, variant = 'default', size = 'md', className = '' }: BadgeProps) {
  const baseStyles: React.CSSProperties = {
    display: 'inline-flex',
    alignItems: 'center',
    padding: '0.25rem 0.75rem',
    borderRadius: '9999px',
    fontWeight: 500,
    border: '1px solid',
    fontSize: '0.75rem',
  }

  const sizes = {
    sm: { padding: '0.125rem 0.5rem', fontSize: '0.625rem' },
    md: { padding: '0.25rem 0.75rem', fontSize: '0.75rem' },
    lg: { padding: '0.375rem 1rem', fontSize: '0.875rem' },
  }

  const variants = {
    default: {
      backgroundColor: 'var(--color-code-bg)',
      color: 'var(--color-muted)',
      borderColor: 'var(--color-border)',
    },
    accent: {
      backgroundColor: 'color-mix(in oklch, var(--color-accent), transparent 90%)',
      color: 'var(--color-accent)',
      borderColor: 'color-mix(in oklch, var(--color-accent), transparent 80%)',
    },
    success: {
      backgroundColor: 'color-mix(in oklch, var(--color-success), transparent 90%)',
      color: 'var(--color-success)',
      borderColor: 'color-mix(in oklch, var(--color-success), transparent 80%)',
    },
    error: {
      backgroundColor: 'color-mix(in oklch, var(--color-error), transparent 90%)',
      color: 'var(--color-error)',
      borderColor: 'color-mix(in oklch, var(--color-error), transparent 80%)',
    },
  }

  return (
    <span
      className={className}
      style={{
        ...baseStyles,
        ...sizes[size],
        ...variants[variant],
      }}
    >
      {children}
    </span>
  )
}

export default Badge

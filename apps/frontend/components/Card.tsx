'use client'

import React from 'react'

interface CardProps {
  children: React.ReactNode
  className?: string
  hover?: boolean
  padding?: 'sm' | 'md' | 'lg'
}

export function Card({ children, className = '', hover = true, padding = 'md' }: CardProps) {
  const paddingClass = {
    sm: 'p-4',
    md: 'p-6',
    lg: 'p-8',
  }[padding]

  return (
    <div
      className={`card ${paddingClass} ${hover ? 'hover:border-accent hover:-translate-y-1' : ''} ${className}`}
      style={{
        backgroundColor: 'var(--color-card-bg)',
        borderColor: 'var(--color-border)',
        borderRadius: '0.75rem',
        transition: 'all 0.3s var(--transition-timing)',
        ...(hover && {
          '--hover-shadow': '0 20px 40px color-mix(in oklch, var(--color-accent), transparent 85%)',
        } as React.CSSProperties),
      }}
    >
      {children}
    </div>
  )
}

interface CardHeaderProps {
  children: React.ReactNode
  className?: string
}

export function CardHeader({ children, className = '' }: CardHeaderProps) {
  return (
    <div className={`mb-4 ${className}`}>
      {children}
    </div>
  )
}

interface CardTitleProps {
  children: React.ReactNode
  className?: string
  style?: React.CSSProperties
}

export function CardTitle({ children, className = '', style }: CardTitleProps) {
  return (
    <h3 className={`text-lg font-semibold mb-2 ${className}`} style={{ ...{ color: 'var(--color-text)' }, ...style }}>
      {children}
    </h3>
  )
}

interface CardDescriptionProps {
  children: React.ReactNode
  className?: string
}

export function CardDescription({ children, className = '' }: CardDescriptionProps) {
  return (
    <p className={`text-sm ${className}`} style={{ color: 'var(--color-muted)' }}>
      {children}
    </p>
  )
}

interface CardContentProps {
  children: React.ReactNode
  className?: string
}

export function CardContent({ children, className = '' }: CardContentProps) {
  return (
    <div className={className}>
      {children}
    </div>
  )
}

interface CardFooterProps {
  children: React.ReactNode
  className?: string
}

export function CardFooter({ children, className = '' }: CardFooterProps) {
  return (
    <div className={`mt-4 pt-4 border-t ${className}`} style={{ borderColor: 'var(--color-border)' }}>
      {children}
    </div>
  )
}

export default Card

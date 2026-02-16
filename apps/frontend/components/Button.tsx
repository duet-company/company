'use client'

import React from 'react'

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  children: React.ReactNode
  variant?: 'primary' | 'secondary' | 'ghost'
  size?: 'sm' | 'md' | 'lg'
  isLoading?: boolean
  leftIcon?: React.ReactNode
  rightIcon?: React.ReactNode
}

export function Button({
  children,
  variant = 'primary',
  size = 'md',
  isLoading = false,
  leftIcon,
  rightIcon,
  className = '',
  disabled,
  style,
  ...props
}: ButtonProps) {
  const baseStyles: React.CSSProperties = {
    display: 'inline-flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '0.5rem',
    fontWeight: 600,
    textDecoration: 'none',
    cursor: disabled || isLoading ? 'not-allowed' : 'pointer',
    transition: 'all 0.3s var(--transition-timing)',
    border: '2px solid transparent',
    textBox: 'trim-both cap alphabetic',
    opacity: isLoading ? 0.7 : 1,
  }

  const sizes = {
    sm: { padding: '0.5rem 1rem', fontSize: '0.875rem' },
    md: { padding: '0.75rem 1.5rem', fontSize: '1rem' },
    lg: { padding: '1rem 2rem', fontSize: '1.125rem' },
  }

  const variants = {
    primary: {
      backgroundColor: 'var(--color-accent)',
      color: 'white',
    },
    secondary: {
      backgroundColor: 'transparent',
      color: 'var(--color-accent)',
      borderColor: 'var(--color-accent)',
    },
    ghost: {
      backgroundColor: 'transparent',
      color: 'var(--color-text)',
    },
  }

  const mergedStyle: React.CSSProperties = {
    ...baseStyles,
    ...sizes[size],
    ...variants[variant],
    ...(variant === 'primary' && !disabled && {
      '--hover-bg': 'var(--color-accent-hover)',
      '--hover-transform': 'translateY(-2px)',
      '--hover-shadow': '0 10px 20px color-mix(in oklch, var(--color-accent), transparent 80%)',
    } as React.CSSProperties),
    ...(variant === 'secondary' && !disabled && {
      '--hover-bg': 'var(--color-accent)',
      '--hover-color': 'white',
    } as React.CSSProperties),
    ...style,
  }

  return (
    <button
      className={className}
      style={mergedStyle}
      disabled={disabled || isLoading}
      {...props}
    >
      {isLoading ? (
        <>
          <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
          </svg>
          Loading...
        </>
      ) : (
        <>
          {leftIcon}
          {children}
          {rightIcon}
        </>
      )}
    </button>
  )
}

export default Button

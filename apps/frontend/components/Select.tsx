'use client'

import React, { forwardRef } from 'react'

interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  label?: string
  error?: string
  helperText?: string
  options: Array<{ value: string; label: string }>
}

export const Select = forwardRef<HTMLSelectElement, SelectProps>(({
  label,
  error,
  helperText,
  options,
  className = '',
  id,
  ...props
}, ref) => {
  const inputId = id || `select-${Math.random().toString(36).substr(2, 9)}`

  return (
    <div className="w-full">
      {label && (
        <label
          htmlFor={inputId}
          className="block text-sm font-medium mb-2"
          style={{ color: 'var(--color-text)' }}
        >
          {label}
        </label>
      )}
      <select
        ref={ref}
        id={inputId}
        className={`w-full p-3 rounded-lg border outline-none transition-colors ${
          error ? 'border-red-500' : 'border-var(--color-border)'
        } focus:border-accent focus:ring-2 focus:ring-accent/20 ${className}`}
        style={{
          backgroundColor: 'var(--color-card-bg)',
          color: 'var(--color-text)',
          borderColor: error ? 'var(--color-error)' : 'var(--color-border)',
        }}
        aria-invalid={error ? 'true' : undefined}
        aria-describedby={error ? `${inputId}-error` : helperText ? `${inputId}-helper` : undefined}
        {...props}
      >
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
      {error && (
        <p
          id={`${inputId}-error`}
          className="mt-2 text-sm"
          style={{ color: 'var(--color-error)' }}
          role="alert"
        >
          {error}
        </p>
      )}
      {helperText && !error && (
        <p id={`${inputId}-helper`} className="mt-2 text-sm" style={{ color: 'var(--color-muted)' }}>
          {helperText}
        </p>
      )}
    </div>
  )
})

Select.displayName = 'Select'

export default Select

'use client'

import React, { useState, useCallback } from 'react'

interface QueryEditorProps {
  value?: string
  onChange?: (value: string) => void
  placeholder?: string
  readOnly?: boolean
  onExecute?: (query: string) => void
}

export function QueryEditor({
  value = '',
  onChange,
  placeholder = 'SELECT * FROM users WHERE active = true',
  readOnly = false,
  onExecute,
}: QueryEditorProps) {
  const [query, setQuery] = useState(value)
  const [isExecuting, setIsExecuting] = useState(false)

  const handleChange = useCallback(
    (e: React.ChangeEvent<HTMLTextAreaElement>) => {
      const newValue = e.target.value
      setQuery(newValue)
      onChange?.(newValue)
    },
    [onChange]
  )

  const handleExecute = useCallback(async () => {
    if (!query.trim() || isExecuting) return

    setIsExecuting(true)
    try {
      await onExecute?.(query)
    } finally {
      setIsExecuting(false)
    }
  }, [query, isExecuting, onExecute])

  const handleKeyPress = useCallback(
    (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
      if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
        e.preventDefault()
        handleExecute()
      }
    },
    [handleExecute]
  )

  return (
    <div className="query-editor">
      <div
        className="query-editor-wrapper"
        style={{
          position: 'relative',
          border: '1px solid var(--color-border)',
          borderRadius: '0.5rem',
          overflow: 'hidden',
        }}
      >
        <textarea
          value={query}
          onChange={handleChange}
          onKeyDown={handleKeyPress}
          placeholder={placeholder}
          readOnly={readOnly}
          style={{
            width: '100%',
            minHeight: '200px',
            padding: '1rem',
            fontFamily: 'var(--font-mono)',
            fontSize: '0.875rem',
            lineHeight: '1.6',
            border: 'none',
            outline: 'none',
            resize: 'vertical',
            backgroundColor: 'var(--color-code-bg)',
            color: 'var(--color-text)',
            caretColor: 'var(--color-accent)',
          }}
        />

        {!readOnly && (
          <div
            style={{
              position: 'absolute',
              bottom: '1rem',
              right: '1rem',
              display: 'flex',
              gap: '0.5rem',
            }}
          >
            <button
              onClick={handleExecute}
              disabled={!query.trim() || isExecuting}
              className="btn btn-primary"
              style={{
                padding: '0.5rem 1rem',
                fontSize: '0.875rem',
                opacity: !query.trim() ? 0.5 : 1,
              }}
              title="Execute query (⌘/Ctrl + Enter)"
            >
              {isExecuting ? 'Executing...' : 'Execute Query'}
            </button>
          </div>
        )}
      </div>

      <div
        style={{
          marginTop: '0.5rem',
          fontSize: '0.75rem',
          color: 'var(--color-muted)',
        }}
      >
        <span>Press</span>
        <kbd
          style={{
            display: 'inline-block',
            padding: '0.125rem 0.375rem',
            margin: '0 0.25rem',
            fontSize: '0.7rem',
            fontFamily: 'var(--font-mono)',
            background: 'var(--color-code-bg)',
            border: '1px solid var(--color-border)',
            borderRadius: '0.25rem',
          }}
        >
          ⌘/Ctrl + Enter
        </kbd>
        <span>to execute query</span>
      </div>
    </div>
  )
}

// Syntax highlighter for SQL keywords
export function SQLHighlighter({ sql }: { sql: string }) {
  const highlightSQL = (text: string) => {
    const keywords = [
      'SELECT',
      'FROM',
      'WHERE',
      'AND',
      'OR',
      'ORDER BY',
      'GROUP BY',
      'HAVING',
      'LIMIT',
      'OFFSET',
      'JOIN',
      'LEFT JOIN',
      'RIGHT JOIN',
      'INNER JOIN',
      'OUTER JOIN',
      'INSERT',
      'UPDATE',
      'DELETE',
      'CREATE',
      'DROP',
      'ALTER',
      'TABLE',
      'INDEX',
      'VIEW',
      'DISTINCT',
      'COUNT',
      'SUM',
      'AVG',
      'MIN',
      'MAX',
      'AS',
      'ASC',
      'DESC',
      'UNION',
      'ALL',
      'NOT',
      'NULL',
      'IS',
      'IN',
      'BETWEEN',
      'LIKE',
      'EXISTS',
    ]

    let highlighted = text
    keywords.forEach((keyword) => {
      const regex = new RegExp(`\\b${keyword}\\b`, 'gi')
      highlighted = highlighted.replace(
        regex,
        `<span style="color: var(--color-accent); font-weight: 600;">${keyword}</span>`
      )
    })

    // Highlight strings
    highlighted = highlighted.replace(
      /'[^']*'/g,
      `<span style="color: var(--color-secondary);">'$&'</span>`
    )

    // Highlight numbers
    highlighted = highlighted.replace(
      /\b\d+\b/g,
      `<span style="color: var(--color-error);">$&</span>`
    )

    // Highlight comments
    highlighted = highlighted.replace(
      /(--.*$)/gm,
      `<span style="color: var(--color-muted); font-style: italic;">$1</span>`
    )

    return highlighted
  }

  return (
    <div
      dangerouslySetInnerHTML={{ __html: highlightSQL(sql) }}
      style={{
        fontFamily: 'var(--font-mono)',
        fontSize: '0.875rem',
        lineHeight: '1.6',
        whiteSpace: 'pre-wrap',
        wordBreak: 'break-word',
      }}
    />
  )
}

export default QueryEditor

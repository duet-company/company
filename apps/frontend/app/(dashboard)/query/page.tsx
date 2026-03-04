'use client'

import React, { useState } from 'react'
import { QueryEditor } from '@/components/QueryEditor'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/Card'
import { Button } from '@/components/Button'
import { Badge } from '@/components/Badge'

export default function QueryPage() {
  const [query, setQuery] = useState('SELECT * FROM users WHERE active = true ORDER BY created_at DESC LIMIT 100')
  const [results, setResults] = useState<any[] | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [savedQueries, setSavedQueries] = useState([
    { name: 'Active Users', query: 'SELECT * FROM users WHERE active = true' },
    { name: 'Recent Signups', query: 'SELECT * FROM users ORDER BY created_at DESC LIMIT 10' },
    { name: 'Top Performers', query: 'SELECT * FROM users ORDER BY score DESC LIMIT 20' },
  ])

  const handleExecute = async (sql: string) => {
    setIsLoading(true)
    setError(null)
    setResults(null)

    try {
      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 1000))

      // Mock response data
      const mockResults = [
        { id: 1, name: 'John Doe', email: 'john@example.com', active: true, created_at: '2024-01-15', score: 95 },
        { id: 2, name: 'Jane Smith', email: 'jane@example.com', active: true, created_at: '2024-01-14', score: 88 },
        { id: 3, name: 'Bob Johnson', email: 'bob@example.com', active: true, created_at: '2024-01-13', score: 92 },
        { id: 4, name: 'Alice Williams', email: 'alice@example.com', active: false, created_at: '2024-01-12', score: 79 },
        { id: 5, name: 'Charlie Brown', email: 'charlie@example.com', active: true, created_at: '2024-01-11', score: 85 },
      ]

      setResults(mockResults)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to execute query')
    } finally {
      setIsLoading(false)
    }
  }

  const handleSaveQuery = () => {
    const name = prompt('Enter a name for this query:')
    if (name && query.trim()) {
      setSavedQueries([...savedQueries, { name, query: query.trim() }])
    }
  }

  const handleLoadQuery = (savedQuery: { name: string; query: string }) => {
    setQuery(savedQuery.query)
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2" style={{ fontFamily: 'var(--font-display)' }}>
          Query Editor
        </h1>
        <p style={{ color: 'var(--color-muted)' }}>
          Execute SQL queries against your ClickHouse database
        </p>
      </div>

      <div className="grid-auto-fit gap-6">
        {/* Query Editor */}
        <Card className="md:col-span-2">
          <CardHeader>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <CardTitle>SQL Query</CardTitle>
              <div style={{ display: 'flex', gap: '0.5rem' }}>
                <Button variant="secondary" size="sm" onClick={handleSaveQuery}>
                  Save Query
                </Button>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <QueryEditor
              value={query}
              onChange={setQuery}
              onExecute={handleExecute}
              placeholder="Enter your SQL query here..."
            />
          </CardContent>
        </Card>

        {/* Saved Queries */}
        <Card>
          <CardHeader>
            <CardTitle>Saved Queries</CardTitle>
          </CardHeader>
          <CardContent>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              {savedQueries.map((savedQuery, index) => (
                <button
                  key={index}
                  onClick={() => handleLoadQuery(savedQuery)}
                  style={{
                    padding: '0.75rem',
                    border: '1px solid var(--color-border)',
                    borderRadius: '0.5rem',
                    background: 'var(--color-code-bg)',
                    color: 'var(--color-text)',
                    textAlign: 'left',
                    cursor: 'pointer',
                    transition: 'all 0.2s',
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.borderColor = 'var(--color-accent)'
                    e.currentTarget.style.background = 'color-mix(in oklch, var(--color-accent), transparent 90%)'
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.borderColor = 'var(--color-border)'
                    e.currentTarget.style.background = 'var(--color-code-bg)'
                  }}
                >
                  <div style={{ fontWeight: 500, marginBottom: '0.25rem' }}>{savedQuery.name}</div>
                  <div
                    style={{
                      fontSize: '0.75rem',
                      color: 'var(--color-muted)',
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      whiteSpace: 'nowrap',
                    }}
                  >
                    {savedQuery.query}
                  </div>
                </button>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Query Results */}
        <Card className="md:col-span-3">
          <CardHeader>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <CardTitle>Results</CardTitle>
              {isLoading && <Badge>Executing...</Badge>}
              {results && <Badge variant="success">{results.length} rows</Badge>}
            </div>
          </CardHeader>
          <CardContent>
            {isLoading && (
              <div
                style={{
                  textAlign: 'center',
                  padding: '3rem',
                  color: 'var(--color-muted)',
                }}
              >
                <div
                  style={{
                    fontSize: '1.5rem',
                    marginBottom: '0.5rem',
                  }}
                >
                  ⏳
                </div>
                Executing query...
              </div>
            )}

            {error && (
              <div
                style={{
                  padding: '1rem',
                  border: '1px solid var(--color-error)',
                  borderRadius: '0.5rem',
                  background: 'color-mix(in oklch, var(--color-error), transparent 90%)',
                  color: 'var(--color-error)',
                }}
              >
                <div style={{ fontWeight: 600, marginBottom: '0.25rem' }}>Query Error</div>
                <div style={{ fontSize: '0.875rem' }}>{error}</div>
              </div>
            )}

            {results && results.length > 0 && (
              <div style={{ overflowX: 'auto' }}>
                <table>
                  <thead>
                    <tr>
                      {Object.keys(results[0]).map((key) => (
                        <th key={key}>{key}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {results.map((row, index) => (
                      <tr key={index} style={{ borderBottom: '1px solid var(--color-border)' }}>
                        {Object.values(row).map((value, cellIndex) => (
                          <td key={cellIndex} style={{ padding: '0.75rem 1rem', color: 'var(--color-text)' }}>
                            {value === true ? (
                              <Badge variant="success">true</Badge>
                            ) : value === false ? (
                              <Badge variant="error">false</Badge>
                            ) : (
                              String(value)
                            )}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            {!isLoading && !error && !results && (
              <div
                style={{
                  textAlign: 'center',
                  padding: '3rem',
                  color: 'var(--color-muted)',
                }}
              >
                <div
                  style={{
                    fontSize: '1.5rem',
                    marginBottom: '0.5rem',
                  }}
                >
                  📊
                </div>
                Execute a query to see results here
              </div>
            )}
          </CardContent>
        </Card>

        {/* Query History */}
        <Card className="md:col-span-3">
          <CardHeader>
            <CardTitle>Query History</CardTitle>
          </CardHeader>
          <CardContent>
            <div style={{ fontSize: '0.875rem', color: 'var(--color-muted)' }}>
              No recent queries yet. Execute your first query to see history here.
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

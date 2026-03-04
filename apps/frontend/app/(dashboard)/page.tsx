'use client'

import React, { useState, useEffect } from 'react'
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from '@/components/Card'
import { Badge } from '@/components/Badge'
import { StatsCard } from '@/components/Charts'
import { LineChartComponent, BarChartComponent } from '@/components/Charts'

export default function DashboardPage() {
  const [isLoading, setIsLoading] = useState(true)
  const [currentTime, setCurrentTime] = useState(new Date())

  useEffect(() => {
    // Simulate data loading
    const timer = setTimeout(() => setIsLoading(false), 1000)
    return () => clearTimeout(timer)
  }, [])

  useEffect(() => {
    // Update time every minute
    const timer = setInterval(() => setCurrentTime(new Date()), 60000)
    return () => clearInterval(timer)
  }, [])

  // Mock data for charts
  const queryPerformanceData = [
    { time: '00:00', queries: 120, latency: 45 },
    { time: '04:00', queries: 80, latency: 52 },
    { time: '08:00', queries: 350, latency: 38 },
    { time: '12:00', queries: 520, latency: 42 },
    { time: '16:00', queries: 480, latency: 39 },
    { time: '20:00', queries: 410, latency: 41 },
    { time: '23:59', queries: 280, latency: 48 },
  ]

  const agentUsageData = [
    { agent: 'Query Agent', calls: 12400, successRate: 99.2 },
    { agent: 'Design Agent', calls: 8700, successRate: 97.8 },
    { agent: 'Support Agent', calls: 22100, successRate: 98.5 },
    { agent: 'Data Agent', calls: 2000, successRate: 100 },
  ]

  const recentAgents = [
    { name: 'Query Agent', status: 'healthy', calls: '12.4K', latency: '28ms', cpu: '45%', memory: '512MB' },
    { name: 'Design Agent', status: 'healthy', calls: '8.7K', latency: '45ms', cpu: '32%', memory: '384MB' },
    { name: 'Support Agent', status: 'degraded', calls: '22.1K', latency: '89ms', cpu: '78%', memory: '768MB' },
    { name: 'Data Agent', status: 'healthy', calls: '2.0K', latency: '52ms', cpu: '18%', memory: '256MB' },
  ]

  const recentActivity = [
    { id: 1, type: 'query', message: 'Query executed successfully', time: '2 minutes ago', status: 'success' },
    { id: 2, type: 'agent', message: 'Support Agent resolved ticket #1234', time: '5 minutes ago', status: 'success' },
    { id: 3, type: 'query', message: 'Query failed: timeout', time: '8 minutes ago', status: 'error' },
    { id: 4, type: 'agent', message: 'Query Agent auto-scaled to 3 instances', time: '15 minutes ago', status: 'info' },
    { id: 5, type: 'system', message: 'Database backup completed', time: '1 hour ago', status: 'success' },
  ]

  if (isLoading) {
    return (
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '60vh',
          color: 'var(--color-muted)',
        }}
      >
        <div style={{ fontSize: '2rem', marginBottom: '1rem' }}>⏳</div>
        <div>Loading dashboard...</div>
      </div>
    )
  }

  return (
    <div>
      {/* Header */}
      <div className="mb-8">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.5rem' }}>
          <div>
            <h1 className="text-3xl font-bold mb-2" style={{ fontFamily: 'var(--font-display)' }}>
              Dashboard
            </h1>
            <p style={{ color: 'var(--color-muted)' }}>
              Overview of your AI Data Labs deployment
            </p>
          </div>
          <Badge variant="success">System Online</Badge>
        </div>
        <div style={{ fontSize: '0.875rem', color: 'var(--color-muted)' }}>
          Last updated: {currentTime.toLocaleString()}
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid-auto-fit mb-8">
        <StatsCard
          title="Active Agents"
          value="12"
          change="+2 this week"
          trend="up"
        />
        <StatsCard
          title="API Calls (24h)"
          value="45.2K"
          change="+12.5%"
          trend="up"
        />
        <StatsCard
          title="Avg Latency"
          value="45ms"
          change="-3ms"
          trend="down"
        />
        <StatsCard
          title="System Health"
          value="99.9%"
          change="0%"
          trend="neutral"
        />
      </div>

      {/* Charts Section */}
      <div className="grid-auto-fit gap-6 mb-8">
        <Card className="md:col-span-2">
          <CardHeader>
            <CardTitle>Query Performance</CardTitle>
            <CardDescription>Query volume and latency over time</CardDescription>
          </CardHeader>
          <CardContent>
            <LineChartComponent
              data={queryPerformanceData}
              xKey="time"
              yKey="queries"
              title="Query Volume"
              color="var(--color-accent)"
            />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Agent Usage</CardTitle>
            <CardDescription>Calls per agent (24h)</CardDescription>
          </CardHeader>
          <CardContent>
            <BarChartComponent
              data={agentUsageData}
              xKey="agent"
              yKey="calls"
              color="var(--color-secondary)"
            />
          </CardContent>
        </Card>
      </div>

      {/* Main Content */}
      <div className="grid-auto-fit gap-6">
        {/* Agents Table */}
        <Card className="md:col-span-2">
          <CardHeader>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <CardTitle>Agent Status</CardTitle>
                <CardDescription>Real-time agent performance metrics</CardDescription>
              </div>
              <Badge variant="success">4 Online</Badge>
            </div>
          </CardHeader>
          <CardContent>
            <div style={{ overflowX: 'auto' }}>
              <table>
                <thead>
                  <tr>
                    <th>Agent</th>
                    <th>Status</th>
                    <th>Calls (24h)</th>
                    <th>Latency</th>
                    <th>CPU</th>
                    <th>Memory</th>
                  </tr>
                </thead>
                <tbody>
                  {recentAgents.map((agent, i) => (
                    <tr key={i} style={{ borderBottom: '1px solid var(--color-border)' }}>
                      <td style={{ padding: '0.75rem 1rem', color: 'var(--color-text)' }}>{agent.name}</td>
                      <td style={{ padding: '0.75rem 1rem' }}>
                        <Badge variant={agent.status === 'healthy' ? 'success' : 'error'}>
                          {agent.status}
                        </Badge>
                      </td>
                      <td style={{ padding: '0.75rem 1rem', color: 'var(--color-muted)' }}>{agent.calls}</td>
                      <td style={{ padding: '0.75rem 1rem', color: 'var(--color-muted)' }}>{agent.latency}</td>
                      <td style={{ padding: '0.75rem 1rem', color: 'var(--color-muted)' }}>{agent.cpu}</td>
                      <td style={{ padding: '0.75rem 1rem', color: 'var(--color-muted)' }}>{agent.memory}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>

        {/* Recent Activity */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
            <CardDescription>Latest system events</CardDescription>
          </CardHeader>
          <CardContent>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              {recentActivity.map((activity) => (
                <div
                  key={activity.id}
                  style={{
                    padding: '0.75rem',
                    borderRadius: '0.5rem',
                    background: 'var(--color-code-bg)',
                    border: '1px solid var(--color-border)',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.5rem', marginBottom: '0.25rem' }}>
                    <div style={{ fontSize: '1rem' }}>
                      {activity.type === 'query' && '📊'}
                      {activity.type === 'agent' && '🤖'}
                      {activity.type === 'system' && '⚙️'}
                    </div>
                    <div style={{ flex: 1 }}>
                      <div style={{ fontSize: '0.875rem', fontWeight: 500, marginBottom: '0.25rem' }}>
                        {activity.message}
                      </div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--color-muted)' }}>
                        {activity.time}
                      </div>
                    </div>
                    <Badge variant={activity.status === 'success' ? 'success' : activity.status === 'error' ? 'error' : 'info'}>
                      {activity.status}
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Quick Actions */}
        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
            <CardDescription>Common tasks and shortcuts</CardDescription>
          </CardHeader>
          <CardContent>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              <a
                href="/query"
                className="btn btn-primary w-full justify-start"
                style={{ textDecoration: 'none' }}
              >
                📊 New Query
              </a>
              <a
                href="/settings"
                className="btn btn-secondary w-full justify-start"
                style={{ textDecoration: 'none' }}
              >
                ⚙️ Settings
              </a>
              <button className="btn btn-secondary w-full justify-start">
                📋 View Logs
              </button>
              <button className="btn btn-secondary w-full justify-start">
                📈 System Metrics
              </button>
              <button className="btn btn-secondary w-full justify-start">
                🔑 API Keys
              </button>
            </div>
          </CardContent>
        </Card>

        {/* System Health */}
        <Card>
          <CardHeader>
            <CardTitle>System Health</CardTitle>
            <CardDescription>Overall platform status</CardDescription>
          </CardHeader>
          <CardContent>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.25rem' }}>
                  <span style={{ fontSize: '0.875rem', fontWeight: 500 }}>CPU Usage</span>
                  <span style={{ fontSize: '0.875rem', color: 'var(--color-muted)' }}>45%</span>
                </div>
                <div
                  style={{
                    height: '6px',
                    background: 'var(--color-border)',
                    borderRadius: '3px',
                    overflow: 'hidden',
                  }}
                >
                  <div
                    style={{
                      height: '100%',
                      width: '45%',
                      background: 'var(--color-accent)',
                      borderRadius: '3px',
                    }}
                  />
                </div>
              </div>

              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.25rem' }}>
                  <span style={{ fontSize: '0.875rem', fontWeight: 500 }}>Memory Usage</span>
                  <span style={{ fontSize: '0.875rem', color: 'var(--color-muted)' }}>68%</span>
                </div>
                <div
                  style={{
                    height: '6px',
                    background: 'var(--color-border)',
                    borderRadius: '3px',
                    overflow: 'hidden',
                  }}
                >
                  <div
                    style={{
                      height: '100%',
                      width: '68%',
                      background: 'var(--color-secondary)',
                      borderRadius: '3px',
                    }}
                  />
                </div>
              </div>

              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.25rem' }}>
                  <span style={{ fontSize: '0.875rem', fontWeight: 500 }}>Disk Usage</span>
                  <span style={{ fontSize: '0.875rem', color: 'var(--color-muted)' }}>32%</span>
                </div>
                <div
                  style={{
                    height: '6px',
                    background: 'var(--color-border)',
                    borderRadius: '3px',
                    overflow: 'hidden',
                  }}
                >
                  <div
                    style={{
                      height: '100%',
                      width: '32%',
                      background: 'var(--color-success)',
                      borderRadius: '3px',
                    }}
                  />
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

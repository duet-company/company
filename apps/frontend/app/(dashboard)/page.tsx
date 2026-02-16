import { Card, CardHeader, CardTitle, CardContent } from '@/components/Card'
import { Badge } from '@/components/Badge'

export default function DashboardPage() {
  const stats = [
    { label: 'Active Agents', value: '12', change: '+2 this week' },
    { label: 'API Calls (24h)', value: '45.2K', change: '+12.5%' },
    { label: 'Avg Latency', value: '45ms', change: '-3ms' },
    { label: 'System Health', value: '99.9%', change: '0%' },
  ]

  const recentAgents = [
    { name: 'Query Agent', status: 'healthy', calls: '12.4K', latency: '28ms' },
    { name: 'Design Agent', status: 'healthy', calls: '8.7K', latency: '45ms' },
    { name: 'Support Agent', status: 'degraded', calls: '22.1K', latency: '89ms' },
    { name: 'Data Agent', status: 'healthy', calls: '2.0K', latency: '52ms' },
  ]

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2" style={{ fontFamily: 'var(--font-display)' }}>
          Dashboard
        </h1>
        <p style={{ color: 'var(--color-muted)' }}>
          Overview of your AI Data Labs deployment
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid-auto-fit mb-8">
        {stats.map((stat, i) => (
          <Card key={i} padding="lg">
            <CardHeader>
              <CardTitle className="text-sm uppercase tracking-wider" style={{ color: 'var(--color-muted)', fontWeight: 500 }}>
                {stat.label}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-4xl font-bold mb-2" style={{ color: 'var(--color-accent)', fontFamily: 'var(--font-display)' }}>
                {stat.value}
              </div>
              <p className="text-sm" style={{ color: 'var(--color-muted)' }}>
                {stat.change}
              </p>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid-auto-fit gap-6">
        {/* Agents Table */}
        <Card className="md:col-span-2">
          <CardHeader>
            <CardTitle>Agent Status</CardTitle>
          </CardHeader>
          <CardContent>
            <div style={{ overflowX: 'auto' }}>
              <table>
                <thead>
                  <tr>
                    <th>Agent</th>
                    <th>Status</th>
                    <th>API Calls</th>
                    <th>Avg Latency</th>
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
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>

        {/* Quick Actions */}
        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <button className="btn btn-primary w-full justify-start">Deploy New Agent</button>
              <button className="btn btn-secondary w-full justify-start">View Logs</button>
              <button className="btn btn-secondary w-full justify-start">System Metrics</button>
              <button className="btn btn-secondary w-full justify-start">API Keys</button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

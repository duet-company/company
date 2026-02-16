export default function HomePage() {
  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="py-20 md:py-32 border-b" style={{ borderColor: 'var(--color-border)' }}>
        <div className="container">
          <div className="max-w-3xl mx-auto text-center">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full mb-6"
                 style={{ background: 'color-mix(in oklch, var(--color-accent), var(--color-secondary))', color: 'white' }}>
              <span className="badge-accent text-xs">AI Data Labs</span>
            </div>

            <h1 className="mb-6" style={{ fontFamily: 'var(--font-display)' }}>
              Build AI Agents in <span className="gradient-text">Hours</span>, Not Months
            </h1>

            <p className="text-xl mb-8" style={{ color: 'var(--color-muted)' }}>
              AI-first data infrastructure platform. Deploy production-ready agent systems with our pre-built components and best-practice patterns.
            </p>

            <div className="flex flex-wrap gap-4 justify-center">
              <a href="/getting-started" className="btn btn-primary">
                Get Started
              </a>
              <a href="/docs" className="btn btn-secondary">
                Documentation
              </a>
            </div>
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section className="py-20">
        <div className="container">
          <h2 className="text-center mb-12" style={{ fontSize: 'clamp(1.5rem, 4vw, 2rem)', fontFamily: 'var(--font-display)' }}>
            Why Choose AI Data Labs?
          </h2>

          <div className="grid-auto-fit">
            <div className="card">
              <h3>⚡ Instant Setup</h3>
              <p style={{ color: 'var(--color-muted)' }}>
                From zero to production in under 2 hours. Our platform handles infrastructure, scaling, and monitoring automatically.
              </p>
            </div>

            <div className="card">
              <h3>🤖 Pre-Built Agents</h3>
              <p style={{ color: 'var(--color-muted)' }}>
                Query agents, design agents, and support agents ready to deploy. Customize them or build your own with our SDK.
              </p>
            </div>

            <div className="card">
              <h3>🔗 Seamless Integration</h3>
              <p style={{ color: 'var(--color-muted)' }}>
                Connect to ClickHouse, PostgreSQL, Kafka, and more with built-in connectors. No manual wiring required.
              </p>
            </div>

            <div className="card">
              <h3>📊 Real-Time Analytics</h3>
              <p style={{ color: 'var(--color-muted)' }}>
                Built-in observability dashboards. Monitor agent performance, costs, and system health in real-time.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-20" style={{ backgroundColor: 'var(--color-code-bg)' }}>
        <div className="container">
          <div className="grid-auto-fit" style={{ maxWidth: '800px', margin: '0 auto' }}>
            <div className="card text-center">
              <div className="text-4xl font-bold mb-2" style={{ color: 'var(--color-accent)', fontFamily: 'var(--font-display)' }}>
                2h
              </div>
              <div className="badge">Time to Production</div>
            </div>

            <div className="card text-center">
              <div className="text-4xl font-bold mb-2" style={{ color: 'var(--color-accent)', fontFamily: 'var(--font-display)' }}>
                10x
              </div>
              <div className="badge">Faster Development</div>
            </div>

            <div className="card text-center">
              <div className="text-4xl font-bold mb-2" style={{ color: 'var(--color-accent)', fontFamily: 'var(--font-display)' }}>
                99.9%
              </div>
              <div className="badge">Uptime SLA</div>
            </div>

            <div className="card text-center">
              <div className="text-4xl font-bold mb-2" style={{ color: 'var(--color-accent)', fontFamily: 'var(--font-display)' }}>
                $0
              </div>
              <div className="badge">Infrastructure Cost for First 1000 Calls</div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20">
        <div className="container">
          <div className="card text-center max-w-2xl mx-auto">
            <h2 className="mb-4">Ready to Build AI Agents?</h2>
            <p className="mb-6" style={{ color: 'var(--color-muted)' }}>
              Join hundreds of data teams using AI Data Labs to deploy production AI systems faster than ever before.
            </p>
            <div className="flex gap-4 justify-center flex-wrap">
              <a href="/signup" className="btn btn-primary">Start Free Trial</a>
              <a href="/demo" className="btn btn-secondary">Schedule Demo</a>
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}

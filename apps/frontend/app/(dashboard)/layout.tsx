export const metadata = {
  title: 'Dashboard | AI Data Labs',
}

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="min-h-screen">
      {/* Sidebar */}
      <aside className="hidden md:block fixed left-0 top-0 h-full w-64 border-r p-6"
             style={{ borderColor: 'var(--color-border)', backgroundColor: 'var(--color-card-bg)' }}>
        <div className="mb-8">
          <h1 className="text-xl font-bold" style={{ color: 'var(--color-accent)' }}>AI Data Labs</h1>
        </div>

        <nav className="space-y-2">
          <a href="/dashboard" className="flex items-center gap-3 px-3 py-2 rounded-lg bg-accent text-white">Overview</a>
          <a href="/dashboard/agents" className="flex items-center gap-3 px-3 py-2 rounded-lg" style={{ color: 'var(--color-text)' }}>Agents</a>
          <a href="/dashboard/data" className="flex items-center gap-3 px-3 py-2 rounded-lg" style={{ color: 'var(--color-text)' }}>Data</a>
          <a href="/dashboard/analytics" className="flex items-center gap-3 px-3 py-2 rounded-lg" style={{ color: 'var(--color-text)' }}>Analytics</a>
          <a href="/dashboard/settings" className="flex items-center gap-3 px-3 py-2 rounded-lg" style={{ color: 'var(--color-text)' }}>Settings</a>
        </nav>
      </aside>

      {/* Mobile header */}
      <header className="md:hidden sticky top-0 z-50 p-4 border-b flex items-center justify-between"
              style={{ borderColor: 'var(--color-border)', backgroundColor: 'var(--color-bg)' }}>
        <h1 className="text-lg font-bold" style={{ color: 'var(--color-accent)' }}>AI Data Labs</h1>
        <button className="btn btn-ghost btn-icon">☰</button>
      </header>

      {/* Main content */}
      <main className="md:pl-64">
        <div className="container py-8">
          {children}
        </div>
      </main>
    </div>
  )
}

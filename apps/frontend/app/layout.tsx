import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'AI Data Labs | Duet Company',
  description: 'AI-first data infrastructure platform - Hours to Production, Not Months',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}

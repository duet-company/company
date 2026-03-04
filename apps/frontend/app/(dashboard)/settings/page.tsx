'use client'

import React, { useState } from 'react'
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from '@/components/Card'
import { Button } from '@/components/Button'

export default function SettingsPage() {
  const [notifications, setNotifications] = useState({
    email: true,
    push: false,
    slack: true,
  })

  const [preferences, setPreferences] = useState({
    theme: 'system',
    language: 'en',
    timezone: 'UTC',
  })

  const [apiKeys, setApiKeys] = useState([
    { name: 'Production Key', key: 'sk_prod_****', lastUsed: '2 hours ago' },
    { name: 'Development Key', key: 'sk_dev_****', lastUsed: '1 day ago' },
  ])

  const handleNotificationChange = (type: string) => {
    setNotifications((prev) => ({
      ...prev,
      [type]: !prev[type as keyof typeof prev],
    }))
  }

  const handlePreferenceChange = (key: string, value: string) => {
    setPreferences((prev) => ({
      ...prev,
      [key]: value,
    }))
  }

  const handleCreateApiKey = () => {
    const newKey = {
      name: `New API Key ${apiKeys.length + 1}`,
      key: `sk_${Math.random().toString(36).substring(2, 15)}****`,
      lastUsed: 'Never',
    }
    setApiKeys([...apiKeys, newKey])
  }

  const handleDeleteApiKey = (index: number) => {
    setApiKeys(apiKeys.filter((_, i) => i !== index))
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2" style={{ fontFamily: 'var(--font-display)' }}>
          Settings
        </h1>
        <p style={{ color: 'var(--color-muted)' }}>
          Manage your account preferences and configurations
        </p>
      </div>

      <div className="grid-auto-fit gap-6">
        {/* Notifications */}
        <Card>
          <CardHeader>
            <CardTitle>Notifications</CardTitle>
            <CardDescription>Configure how you receive alerts and updates</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {[
                { key: 'email', label: 'Email Notifications', description: 'Receive updates via email' },
                { key: 'push', label: 'Push Notifications', description: 'Get real-time alerts in browser' },
                { key: 'slack', label: 'Slack Integration', description: 'Send notifications to Slack' },
              ].map((item) => (
                <div key={item.key} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <div style={{ fontWeight: 500, marginBottom: '0.25rem' }}>{item.label}</div>
                    <div style={{ fontSize: '0.875rem', color: 'var(--color-muted)' }}>
                      {item.description}
                    </div>
                  </div>
                  <label style={{ position: 'relative', display: 'inline-block', width: '44px', height: '24px' }}>
                    <input
                      type="checkbox"
                      checked={notifications[item.key as keyof typeof notifications]}
                      onChange={() => handleNotificationChange(item.key)}
                      style={{ opacity: 0, width: 0, height: 0 }}
                    />
                    <span
                      style={{
                        position: 'absolute',
                        cursor: 'pointer',
                        top: 0,
                        left: 0,
                        right: 0,
                        bottom: 0,
                        backgroundColor: notifications[item.key as keyof typeof notifications]
                          ? 'var(--color-accent)'
                          : 'var(--color-border)',
                        transition: '0.3s',
                        borderRadius: '24px',
                      }}
                    >
                      <span
                        style={{
                          position: 'absolute',
                          content: '""',
                          height: '18px',
                          width: '18px',
                          left: notifications[item.key as keyof typeof notifications] ? '24px' : '3px',
                          bottom: '3px',
                          backgroundColor: 'white',
                          transition: '0.3s',
                          borderRadius: '50%',
                        }}
                      />
                    </span>
                  </label>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Preferences */}
        <Card>
          <CardHeader>
            <CardTitle>Preferences</CardTitle>
            <CardDescription>Customize your user experience</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 500 }}>
                  Theme
                </label>
                <select
                  value={preferences.theme}
                  onChange={(e) => handlePreferenceChange('theme', e.target.value)}
                  style={{
                    width: '100%',
                    padding: '0.75rem',
                    border: '1px solid var(--color-border)',
                    borderRadius: '0.5rem',
                    backgroundColor: 'var(--color-code-bg)',
                    color: 'var(--color-text)',
                  }}
                >
                  <option value="system">System</option>
                  <option value="light">Light</option>
                  <option value="dark">Dark</option>
                </select>
              </div>

              <div>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 500 }}>
                  Language
                </label>
                <select
                  value={preferences.language}
                  onChange={(e) => handlePreferenceChange('language', e.target.value)}
                  style={{
                    width: '100%',
                    padding: '0.75rem',
                    border: '1px solid var(--color-border)',
                    borderRadius: '0.5rem',
                    backgroundColor: 'var(--color-code-bg)',
                    color: 'var(--color-text)',
                  }}
                >
                  <option value="en">English</option>
                  <option value="es">Español</option>
                  <option value="fr">Français</option>
                  <option value="de">Deutsch</option>
                </select>
              </div>

              <div>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 500 }}>
                  Timezone
                </label>
                <select
                  value={preferences.timezone}
                  onChange={(e) => handlePreferenceChange('timezone', e.target.value)}
                  style={{
                    width: '100%',
                    padding: '0.75rem',
                    border: '1px solid var(--color-border)',
                    borderRadius: '0.5rem',
                    backgroundColor: 'var(--color-code-bg)',
                    color: 'var(--color-text)',
                  }}
                >
                  <option value="UTC">UTC</option>
                  <option value="America/New_York">America/New_York</option>
                  <option value="America/Los_Angeles">America/Los_Angeles</option>
                  <option value="Europe/London">Europe/London</option>
                  <option value="Europe/Berlin">Europe/Berlin</option>
                  <option value="Asia/Tokyo">Asia/Tokyo</option>
                </select>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* API Keys */}
        <Card className="md:col-span-2">
          <CardHeader>
            <CardTitle>API Keys</CardTitle>
            <CardDescription>Manage your API keys for programmatic access</CardDescription>
          </CardHeader>
          <CardContent>
            <div style={{ marginBottom: '1rem' }}>
              <Button onClick={handleCreateApiKey}>+ Create New API Key</Button>
            </div>

            <div style={{ overflowX: 'auto' }}>
              <table>
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Key</th>
                    <th>Last Used</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {apiKeys.map((key, index) => (
                    <tr key={index} style={{ borderBottom: '1px solid var(--color-border)' }}>
                      <td style={{ padding: '0.75rem 1rem', color: 'var(--color-text)' }}>
                        {key.name}
                      </td>
                      <td style={{ padding: '0.75rem 1rem', color: 'var(--color-muted)' }}>
                        <code>{key.key}</code>
                      </td>
                      <td style={{ padding: '0.75rem 1rem', color: 'var(--color-muted)' }}>
                        {key.lastUsed}
                      </td>
                      <td style={{ padding: '0.75rem 1rem' }}>
                        <Button
                          variant="secondary"
                          size="sm"
                          onClick={() => handleDeleteApiKey(index)}
                          style={{
                            padding: '0.5rem 1rem',
                            fontSize: '0.875rem',
                            borderColor: 'var(--color-error)',
                            color: 'var(--color-error)',
                          }}
                        >
                          Delete
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>

        {/* Account */}
        <Card>
          <CardHeader>
            <CardTitle>Account</CardTitle>
            <CardDescription>Manage your account settings</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 500 }}>
                  Email
                </label>
                <input
                  type="email"
                  defaultValue="user@example.com"
                  style={{
                    width: '100%',
                    padding: '0.75rem',
                    border: '1px solid var(--color-border)',
                    borderRadius: '0.5rem',
                    backgroundColor: 'var(--color-code-bg)',
                    color: 'var(--color-text)',
                  }}
                />
              </div>

              <div>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 500 }}>
                  Display Name
                </label>
                <input
                  type="text"
                  defaultValue="John Doe"
                  style={{
                    width: '100%',
                    padding: '0.75rem',
                    border: '1px solid var(--color-border)',
                    borderRadius: '0.5rem',
                    backgroundColor: 'var(--color-code-bg)',
                    color: 'var(--color-text)',
                  }}
                />
              </div>

              <div>
                <Button className="btn-secondary w-full">Change Password</Button>
              </div>

              <div>
                <Button
                  variant="secondary"
                  className="w-full"
                  style={{
                    borderColor: 'var(--color-error)',
                    color: 'var(--color-error)',
                  }}
                >
                  Delete Account
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

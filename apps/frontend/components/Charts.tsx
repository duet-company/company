'use client'

import React from 'react'
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  AreaChart,
  Area,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'

const COLORS = [
  'var(--color-accent)',
  'var(--color-secondary)',
  'var(--color-error)',
  'var(--color-success)',
  '#8b5cf6',
  '#f59e0b',
]

interface ChartProps {
  title?: string
  className?: string
  style?: React.CSSProperties
}

// Line Chart for time series data
export function LineChartComponent({
  data,
  xKey,
  yKey,
  title,
  color = 'var(--color-accent)',
}: {
  data: any[]
  xKey: string
  yKey: string
  title?: string
  color?: string
}) {
  return (
    <div style={{ width: '100%', height: 300 }}>
      {title && <h4 style={{ marginBottom: '1rem', color: 'var(--color-text)' }}>{title}</h4>}
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
          <XAxis
            dataKey={xKey}
            stroke="var(--color-muted)"
            style={{ fontSize: '0.75rem' }}
          />
          <YAxis
            stroke="var(--color-muted)"
            style={{ fontSize: '0.75rem' }}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: 'var(--color-card-bg)',
              border: '1px solid var(--color-border)',
              borderRadius: '0.5rem',
              color: 'var(--color-text)',
            }}
          />
          <Legend />
          <Line
            type="monotone"
            dataKey={yKey}
            stroke={color}
            strokeWidth={2}
            dot={{ fill: color }}
            activeDot={{ r: 6 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}

// Bar Chart for categorical data
export function BarChartComponent({
  data,
  xKey,
  yKey,
  title,
  color = 'var(--color-accent)',
}: {
  data: any[]
  xKey: string
  yKey: string
  title?: string
  color?: string
}) {
  return (
    <div style={{ width: '100%', height: 300 }}>
      {title && <h4 style={{ marginBottom: '1rem', color: 'var(--color-text)' }}>{title}</h4>}
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
          <XAxis
            dataKey={xKey}
            stroke="var(--color-muted)"
            style={{ fontSize: '0.75rem' }}
          />
          <YAxis
            stroke="var(--color-muted)"
            style={{ fontSize: '0.75rem' }}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: 'var(--color-card-bg)',
              border: '1px solid var(--color-border)',
              borderRadius: '0.5rem',
              color: 'var(--color-text)',
            }}
          />
          <Legend />
          <Bar dataKey={yKey} fill={color} radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}

// Area Chart for cumulative data
export function AreaChartComponent({
  data,
  xKey,
  yKey,
  title,
  color = 'var(--color-accent)',
}: {
  data: any[]
  xKey: string
  yKey: string
  title?: string
  color?: string
}) {
  return (
    <div style={{ width: '100%', height: 300 }}>
      {title && <h4 style={{ marginBottom: '1rem', color: 'var(--color-text)' }}>{title}</h4>}
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
          <XAxis
            dataKey={xKey}
            stroke="var(--color-muted)"
            style={{ fontSize: '0.75rem' }}
          />
          <YAxis
            stroke="var(--color-muted)"
            style={{ fontSize: '0.75rem' }}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: 'var(--color-card-bg)',
              border: '1px solid var(--color-border)',
              borderRadius: '0.5rem',
              color: 'var(--color-text)',
            }}
          />
          <Legend />
          <Area
            type="monotone"
            dataKey={yKey}
            stroke={color}
            fill={color}
            fillOpacity={0.3}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  )
}

// Pie Chart for distribution
export function PieChartComponent({
  data,
  nameKey,
  valueKey,
  title,
}: {
  data: any[]
  nameKey: string
  valueKey: string
  title?: string
}) {
  return (
    <div style={{ width: '100%', height: 300 }}>
      {title && <h4 style={{ marginBottom: '1rem', color: 'var(--color-text)' }}>{title}</h4>}
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={data}
            dataKey={valueKey}
            nameKey={nameKey}
            cx="50%"
            cy="50%"
            innerRadius={60}
            outerRadius={100}
            paddingAngle={5}
            label
          >
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip
            contentStyle={{
              backgroundColor: 'var(--color-card-bg)',
              border: '1px solid var(--color-border)',
              borderRadius: '0.5rem',
              color: 'var(--color-text)',
            }}
          />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </div>
  )
}

// Stats Card for single metric
export function StatsCard({
  title,
  value,
  change,
  trend = 'neutral',
  icon,
}: {
  title: string
  value: string | number
  change?: string
  trend?: 'up' | 'down' | 'neutral'
  icon?: React.ReactNode
}) {
  const trendColor = {
    up: 'var(--color-success)',
    down: 'var(--color-error)',
    neutral: 'var(--color-muted)',
  }[trend]

  return (
    <div className="card" style={{ padding: '1.5rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.75rem' }}>
        <div>
          <div style={{ fontSize: '0.875rem', color: 'var(--color-muted)', marginBottom: '0.25rem' }}>
            {title}
          </div>
          <div
            style={{
              fontSize: '2rem',
              fontWeight: 700,
              color: 'var(--color-text)',
              fontFamily: 'var(--font-display)',
            }}
          >
            {value}
          </div>
        </div>
        {icon && (
          <div
            style={{
              padding: '0.5rem',
              borderRadius: '0.5rem',
              background: 'color-mix(in oklch, var(--color-accent), transparent 90%)',
              color: 'var(--color-accent)',
            }}
          >
            {icon}
          </div>
        )}
      </div>
      {change && (
        <div style={{ fontSize: '0.875rem', color: trendColor, display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
          {trend === 'up' && <span>↑</span>}
          {trend === 'down' && <span>↓</span>}
          {change}
        </div>
      )}
    </div>
  )
}

export default LineChartComponent

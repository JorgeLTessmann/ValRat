'use client'

import { Area, AreaChart, ResponsiveContainer, XAxis, YAxis, Tooltip } from 'recharts'

interface PortfolioChartProps {
  data: { date: string; value: number }[]
  isVisible?: boolean
}

export function PortfolioChart({ data, isVisible = true }: PortfolioChartProps) {
  if (!isVisible) {
    return (
      <div className="h-full w-full flex items-center justify-center bg-secondary/30 rounded-xl">
        <span className="text-muted-foreground text-sm">Dados ocultos</span>
      </div>
    )
  }

  const formatValue = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
      notation: 'compact',
      maximumFractionDigits: 1
    }).format(value)
  }

  const formatDate = (date: string) => {
    return new Intl.DateTimeFormat('pt-BR', {
      day: '2-digit',
      month: 'short'
    }).format(new Date(date))
  }

  return (
    <ResponsiveContainer width="100%" height="100%">
      <AreaChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
        <defs>
          <linearGradient id="goldGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#D4AF37" stopOpacity={0.3} />
            <stop offset="95%" stopColor="#D4AF37" stopOpacity={0} />
          </linearGradient>
        </defs>
        <XAxis
          dataKey="date"
          tickFormatter={formatDate}
          axisLine={false}
          tickLine={false}
          tick={{ fontSize: 11, fill: '#6B7280' }}
          interval="preserveStartEnd"
          minTickGap={50}
        />
        <YAxis
          tickFormatter={formatValue}
          axisLine={false}
          tickLine={false}
          tick={{ fontSize: 11, fill: '#6B7280' }}
          width={70}
          domain={['dataMin - 1000', 'dataMax + 1000']}
        />
        <Tooltip
          content={({ active, payload }) => {
            if (active && payload && payload.length) {
              const data = payload[0].payload
              return (
                <div className="bg-card border border-border rounded-lg shadow-lg p-3">
                  <p className="text-xs text-muted-foreground mb-1">
                    {new Intl.DateTimeFormat('pt-BR', {
                      day: '2-digit',
                      month: 'long',
                      year: 'numeric'
                    }).format(new Date(data.date))}
                  </p>
                  <p className="text-sm font-semibold text-foreground">
                    {new Intl.NumberFormat('pt-BR', {
                      style: 'currency',
                      currency: 'BRL'
                    }).format(data.value)}
                  </p>
                </div>
              )
            }
            return null
          }}
        />
        <Area
          type="monotone"
          dataKey="value"
          stroke="#D4AF37"
          strokeWidth={2}
          fill="url(#goldGradient)"
        />
      </AreaChart>
    </ResponsiveContainer>
  )
}

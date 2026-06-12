'use client'

import { Area, AreaChart, ResponsiveContainer, XAxis, YAxis, Tooltip } from 'recharts'

interface PortfolioChartProps {
  data: { date: string; value: number }[]
  isVisible?: boolean
}

export function PortfolioChart({ data, isVisible = true }: PortfolioChartProps) {
  if (!isVisible) {
    return (
      <div className="h-full w-full flex flex-col items-center justify-center bg-muted/40 border border-border/40 rounded-xl transition-all duration-200">
        <span className="text-muted-foreground text-xs font-medium tracking-wide uppercase">
          Dados ocultos
        </span>
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
      <AreaChart data={data} margin={{ top: 12, right: 12, left: -12, bottom: 0 }}>
        <defs>
          <linearGradient id="chartGradient" x1="0" y1="0" x2="0" y2="1">
            {/* O gradiente agora utiliza a cor primária do seu tema de forma fluida */}
            <stop offset="0%" stopColor="var(--primary)" stopOpacity={0.2} />
            <stop offset="100%" stopColor="var(--primary)" stopOpacity={0.0} />
          </linearGradient>
        </defs>
        <XAxis
          dataKey="date"
          tickFormatter={formatDate}
          axisLine={false}
          tickLine={false}
          className="text-[11px] font-medium"
          stroke="currentColor"
          tick={{ fill: 'var(--muted-foreground)', opacity: 0.8 }}
          dy={10}
          interval="preserveStartEnd"
          minTickGap={45}
        />
        <YAxis
          tickFormatter={formatValue}
          axisLine={false}
          tickLine={false}
          className="text-[11px] font-medium"
          stroke="currentColor"
          tick={{ fill: 'var(--muted-foreground)', opacity: 0.8 }}
          width={65}
          domain={['dataMin - 1000', 'dataMax + 1000']}
        />
        <Tooltip
          cursor={{ stroke: 'var(--border)', strokeWidth: 1, strokeDasharray: '4 4' }}
          content={({ active, payload }) => {
            if (active && payload && payload.length) {
              const currentData = payload[0].payload
              return (
                <div className="bg-popover border border-border/80 rounded-lg shadow-md p-3 transition-all backdrop-blur-sm">
                  <p className="text-[10px] uppercase font-bold tracking-wider text-muted-foreground mb-1">
                    {new Intl.DateTimeFormat('pt-BR', {
                      day: '2-digit',
                      month: 'long',
                      year: 'numeric'
                    }).format(new Date(currentData.date))}
                  </p>
                  <p className="text-sm font-semibold tracking-tight text-popover-foreground">
                    {new Intl.NumberFormat('pt-BR', {
                      style: 'currency',
                      currency: 'BRL'
                    }).format(currentData.value)}
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
          stroke="var(--primary)"
          strokeWidth={2}
          activeDot={{ r: 4, stroke: 'var(--background)', strokeWidth: 2 }}
          fill="url(#chartGradient)"
        />
      </AreaChart>
    </ResponsiveContainer>
  )
}
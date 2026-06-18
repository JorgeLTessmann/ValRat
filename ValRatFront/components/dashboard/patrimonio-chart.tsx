'use client'

import { useMemo } from 'react'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  Legend
} from 'recharts'
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle
} from '@/components/ui/card'

interface ComparisonItem {
  date: string
  carteira: number
  cdi: number
  ibov: number
}

interface Props {
  historico: ComparisonItem[]
}

export function PatrimonioChart({ historico }: Props) {
  
  // 1. GARANTE A ORDENAÇÃO CRONOLÓGICA (Resolve o sumiço dos dados de 2020)
  const dadosOrdenados = useMemo(() => {
    if (!historico || historico.length === 0) return []

    // Faz uma cópia do array e ordena do mais antigo (2020) para o mais recente (2026)
    return [...historico].sort((a, b) => {
      const dataA = new Date(a.date).getTime()
      const dataB = new Date(b.date).getTime()
      return dataA - dataB
    })
  }, [historico])

  // 2. FORMATADOR PARA PERCENTUAL (%)
  const formatPercentage = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'percent',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(value / 100)
  }

  // 3. CÁLCULO DINÂMICO DE LIMITES (Baseado nos dados já ordenados)
  const chartBounds = useMemo(() => {
    if (dadosOrdenados.length === 0) return { min: 80, max: 120 }
    
    let allValues: number[] = []
    dadosOrdenados.forEach(item => {
      if (typeof item.carteira === 'number') allValues.push(item.carteira)
      if (typeof item.cdi === 'number') allValues.push(item.cdi)
      if (typeof item.ibov === 'number') allValues.push(item.ibov)
    })

    if (allValues.length === 0) return { min: 80, max: 120 }

    const min = Math.min(...allValues)
    const max = Math.max(...allValues)
    
    // Margem de folga de 5% para o gráfico respirar
    const padding = (max - min) * 0.05 || 5
    
    return {
      min: Math.floor(min - padding), 
      max: Math.ceil(max + padding)
    }
  }, [dadosOrdenados])

  return (
    <Card className="border-border/60 shadow-sm bg-card transition-all duration-200">
      <CardHeader className="pb-2">
        <CardTitle className="text-lg font-semibold tracking-tight text-foreground">
          Performance da Carteira (Base Retroativa)
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-[400px] w-full pt-4">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart 
              data={dadosOrdenados} // Consumindo os dados tratados e ordenados
              margin={{ top: 10, right: 20, left: 15, bottom: 5 }}
            >
              <CartesianGrid
                strokeDasharray="4 4"
                stroke="var(--border)"
                opacity={0.4}
                vertical={false}
              />
              
              <XAxis
                dataKey="date"
                axisLine={false}
                tickLine={false}
                dy={10}
                stroke="currentColor"
                tick={{ fill: 'var(--muted-foreground)', fontSize: 11, opacity: 0.8 }}
              />
              
              <YAxis
                axisLine={false}
                tickLine={false}
                dx={-10}
                stroke="currentColor"
                domain={[chartBounds.min, chartBounds.max]}
                tickFormatter={(value) => `${Math.round(value)}%`}
                tick={{ fill: 'var(--muted-foreground)', fontSize: 11, opacity: 0.8 }}
                width={60}
              />
              
              <Tooltip
                cursor={{ stroke: 'var(--border)', strokeWidth: 1, strokeDasharray: '4 4' }}
                shared={true}
                formatter={(value) => [formatPercentage(Number(value)), '']}
                contentStyle={{
                  borderRadius: 'var(--radius, 8px)',
                  border: '1px solid var(--border)',
                  backgroundColor: 'var(--popover)',
                  color: 'var(--popover-foreground)',
                  boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
                  padding: '10px 14px',
                  fontSize: '13px'
                }}
                labelStyle={{
                  fontWeight: '600',
                  color: 'var(--muted-foreground)',
                  fontSize: '11px',
                  textTransform: 'uppercase',
                  letterSpacing: '0.05em',
                  marginBottom: '4px'
                }}
              />
              
              <Legend 
                verticalAlign="top"
                height={36}
                iconType="circle"
                iconSize={8}
                wrapperStyle={{
                  fontSize: '12px',
                  fontWeight: '500',
                  color: 'var(--foreground)',
                  paddingBottom: '16px'
                }}
              />
              
              {/* Linha Principal: Carteira */}
              <Line
                type="monotone"
                dataKey="carteira"
                stroke="var(--primary)"
                strokeWidth={3}
                dot={false}
                name="Sua Carteira"
                connectNulls={true}
                activeDot={{
                  r: 5,
                  stroke: 'var(--background)',
                  strokeWidth: 2
                }}
              />
              
              {/* Linha de Benchmark: CDI */}
              <Line
                type="monotone"
                dataKey="cdi"
                stroke="#10b981"
                strokeWidth={2}
                strokeDasharray="4 4"
                dot={false}
                name="CDI"
                connectNulls={true}
                activeDot={{ r: 4 }}
              />
              
              {/* Linha de Benchmark: Ibovespa */}
              <Line
                type="monotone"
                dataKey="ibov"
                stroke="#f59e0b"
                strokeWidth={2}
                dot={false}
                name="Ibovespa"
                connectNulls={true}
                activeDot={{ r: 4 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  )
}
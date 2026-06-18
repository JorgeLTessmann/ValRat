'use client'

import { useMemo } from 'react'
import { Area, AreaChart, ResponsiveContainer, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts'

interface PortfolioChartProps {
  data: { 
    date: string; 
    value: number;       // Mapeado para o Patrimônio Total no mês
    investido?: number;  // Opcional: Valor investido acumulado no mês
    lucro?: number;      // Opcional: Lucro acumulado no mês
  }[]
  isVisible?: boolean
}

export function PortfolioChart({ data, isVisible = true }: PortfolioChartProps) {
  console.log("[DEBUG RAIO-X] Total de pontos mensais recebidos:", data?.length)
  
  // 1. Garante a ordenação cronológica rigorosa dos meses
  const dadosOrdenados = useMemo(() => {
    if (!data || data.length === 0) return []

    return [...data].sort((a, b) => {
      const dataA = new Date(a.date.split('T')[0]).getTime()
      const dataB = new Date(b.date.split('T')[0]).getTime()
      return dataA - dataB
    })
  }, [data])

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

  const formatCurrencyFull = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value)
  }

  // 2. Formata o Eixo X para exibir apenas o Mês Extenso Curto / Ano (Ex: Jan/24)
  const formatDate = (dateString: string) => {
    const [ano, mes] = dateString.split('T')[0].split('-')
    const dataObjeto = new Date(Number(ano), Number(mes) - 1, 1)
    
    return new Intl.DateTimeFormat('pt-BR', {
      month: 'short',
      year: '2-digit'
    }).format(dataObjeto)
  }

  return (
    <ResponsiveContainer width="100%" height="100%">
      <AreaChart data={dadosOrdenados} margin={{ top: 12, right: 12, left: -12, bottom: 0 }}>
        <defs>
          <linearGradient id="chartGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="var(--primary)" stopOpacity={0.15} />
            <stop offset="100%" stopColor="var(--primary)" stopOpacity={0.0} />
          </linearGradient>
        </defs>

        {/* Linhas de grade discretas para ajudar a ler a evolução */}
        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--border)" opacity={0.3} />
        
        <XAxis
          dataKey="date"
          type="category"
          tickFormatter={formatDate}
          axisLine={false}
          tickLine={false}
          className="text-[11px] font-medium"
          stroke="currentColor"
          tick={{ fill: 'var(--muted-foreground)', opacity: 0.8 }}
          dy={10}
          interval="preserveStart" 
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
          // Ajusta o respiro do topo e fundo do gráfico de forma inteligente
          domain={['dataMin - 500', 'dataMax + 500']}
        />
        
        <Tooltip
          cursor={{ stroke: 'var(--border)', strokeWidth: 1, strokeDasharray: '4 4' }}
          content={({ active, payload }) => {
            if (active && payload && payload.length) {
              const currentData = payload[0].payload
              const [ano, mes] = currentData.date.split('T')[0].split('-')
              const dataTooltip = new Date(Number(ano), Number(mes) - 1, 1)

              // Calcula o lucro caso a propriedade não venha explícita do backend
              const patrimonio = currentData.value || 0
              const investido = currentData.investido || patrimonio
              const lucro = currentData.lucro !== undefined ? currentData.lucro : (patrimonio - investido)

              return (
                <div className="bg-popover border border-border/80 rounded-lg shadow-md p-3 transition-all backdrop-blur-sm min-w-[180px]">
                  <p className="text-[10px] uppercase font-bold tracking-wider text-muted-foreground mb-2 border-b border-border/60 pb-1">
                    {new Intl.DateTimeFormat('pt-BR', {
                      month: 'long',
                      year: 'numeric'
                    }).format(dataTooltip)}
                  </p>
                  
                  <div className="space-y-1">
                    <div className="flex justify-between items-center gap-4">
                      <span className="text-[11px] text-muted-foreground">Patrimônio:</span>
                      <span className="text-xs font-semibold text-popover-foreground">
                        {formatCurrencyFull(patrimonio)}
                      </span>
                    </div>

                    {currentData.investido && (
                      <div className="flex justify-between items-center gap-4">
                        <span className="text-[11px] text-muted-foreground">Investido:</span>
                        <span className="text-xs font-medium text-muted-foreground">
                          {formatCurrencyFull(investido)}
                        </span>
                      </div>
                    )}

                    <div className="flex justify-between items-center gap-4 border-t border-border/40 pt-1 mt-1">
                      <span className="text-[11px] text-muted-foreground">Rendimento:</span>
                      <span className={`text-xs font-bold ${lucro >= 0 ? 'text-emerald-500' : 'text-red-500'}`}>
                        {lucro >= 0 ? '+' : ''}{formatCurrencyFull(lucro)}
                      </span>
                    </div>
                  </div>
                </div>
              )
            }
            return null
          }}
        />
        
        {/* Linha Principal: Patrimônio Líquido Flutuante */}
        <Area
          type="monotone"
          dataKey="value"
          stroke="var(--primary)"
          strokeWidth={2}
          activeDot={{ r: 5, stroke: 'var(--background)', strokeWidth: 2 }}
          fill="url(#chartGradient)"
          connectNulls={true}
        />
      </AreaChart>
    </ResponsiveContainer>
  )
}
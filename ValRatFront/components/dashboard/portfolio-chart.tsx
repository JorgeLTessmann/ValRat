'use client'

import { useEffect, useMemo, useState, useRef } from 'react'
import { Area, AreaChart, ResponsiveContainer, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts'
import { RefreshCw, Loader2 } from 'lucide-react'
import { useAuth } from '@/hooks/use-auth'

interface PortfolioChartProps {
  data: { 
    date: string; 
    value: number;       
    investido?: number;  
    lucro?: number;      
  }[]
  isVisible?: boolean
  onDataRefresh?: (novosDados: { date: string; value: number; investido?: number; lucro?: number }[]) => void
}

function isHoje(dateString: string) {
  const hoje = new Date()
  const hojeStr = `${hoje.getFullYear()}-${String(hoje.getMonth() + 1).padStart(2, '0')}-${String(hoje.getDate()).padStart(2, '0')}`
  return dateString.split('T')[0] === hojeStr
}

export function PortfolioChart({ data, isVisible = true, onDataRefresh }: PortfolioChartProps) {
  const { currentUser } = useAuth()
  const [dadosLocais, setDadosLocais] = useState(data)
  const [recarregando, setRecarregando] = useState(false)
  const [erroReload, setErroReload] = useState<string | null>(null)
  
  // Referência para guardar o ID do setInterval do Polling
  const pollingRef = useRef<NodeJS.Timeout | null>(null)

  useEffect(() => {
    setDadosLocais(data)
  }, [data])

  // Limpa qualquer polling ativo se o componente for desmontado da tela
  useEffect(() => {
    return () => {
      if (pollingRef.current) clearInterval(pollingRef.current)
    }
  }, [])

  // Função que busca o estado atualizado do histórico no banco
  const buscarHistoricoAtualizado = async (userEmail: string) => {
    try {
      const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'https://valrat.onrender.com'
      const response = await fetch(`${baseUrl}/historico`, {
        method: 'GET',
        headers: { 'X-User-Email': userEmail }
      })

      if (response.ok) {
        const historicoNovo = await response.json()
        const dadosFormatados = (Array.isArray(historicoNovo) ? historicoNovo : []).map((item: any) => ({
          date: item.date,
          value: item.carteira ?? item.value ?? 0,
          investido: item.investido,
          lucro: item.lucro,
        }))
        
        setDadosLocais(dadosFormatados)
        onDataRefresh?.(dadosFormatados)
      }
    } catch (err) {
      console.error('[Polling] Erro ao buscar atualização do histórico:', err)
    }
  }

  const handleReload = async () => {
    const userEmail = currentUser?.email ?? null

    if (!userEmail) {
      setErroReload('Usuário não identificado.')
      return
    }

    // Isola o loading apenas no card do gráfico, liberando o resto do app
    setRecarregando(true)
    setErroReload(null)

    try {
      const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'https://valrat.onrender.com'
      const headers = { 'X-User-Email': userEmail }

      // Dispara a rota assíncrona do backend (que responde 202 imediatamente)
      const recalculoResp = await fetch(`${baseUrl}/historico/recalcular-total`, { 
        method: 'POST', 
        headers 
      })
      
      if (!recalculoResp.ok) {
        throw new Error(`Falha ao iniciar recálculo (status ${recalculoResp.status})`)
      }

      // Se o polling antigo já estava rodando por algum motivo, limpa ele
      if (pollingRef.current) clearInterval(pollingRef.current)

      // Inicia o Polling Inteligente: atualiza o gráfico a cada 3 segundos enquanto processa
      let tentativas = 0
      pollingRef.current = setInterval(async () => {
        tentativas++
        await buscarHistoricoAtualizado(userEmail)
        
        // Finaliza o loading visual após 15 segundos (ou 5 ciclos), mas deixa o backend terminando em paz
        if (tentativas >= 5) {
          if (pollingRef.current) clearInterval(pollingRef.current)
          setRecarregando(false)
        }
      }, 3000)

    } catch (error) {
      console.error('[PortfolioChart] Erro ao disparar recálculo:', error)
      setErroReload('Não foi possível atualizar o gráfico agora.')
      setRecarregando(false)
    }
  }

  const dadosOrdenados = useMemo(() => {
    if (!dadosLocais || dadosLocais.length === 0) return []

    return [...dadosLocais].sort((a, b) => {
      const dataA = new Date(a.date.split('T')[0]).getTime()
      const dataB = new Date(b.date.split('T')[0]).getTime()
      return dataA - dataB
    })
  }, [dadosLocais])

  const ultimoIndex = dadosOrdenados.length - 1

  if (!isVisible) {
    return (
      <div className="h-full w-full flex flex-col items-center justify-center bg-muted/40 border border-border/40 rounded-xl">
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

  const formatDate = (dateString: string) => {
    if (!dateString) return ''
    const [ano, mes] = dateString.split('T')[0].split('-')
    const dataObjeto = new Date(Number(ano), Number(mes) - 1, 1)
    
    return new Intl.DateTimeFormat('pt-BR', {
      month: 'short',
      year: '2-digit'
    }).format(dataObjeto)
  }

  const renderDot = (props: any) => {
    const { cx, cy, index } = props
    const ehUltimoPonto = index === ultimoIndex

    if (!ehUltimoPonto) return <g key={`dot-${index}`} />

    return (
      <g key={`dot-${index}`}>
        <circle cx={cx} cy={cy} r={7} fill="var(--primary)" opacity={0.18}>
          <animate attributeName="r" values="6;10;6" dur="2s" repeatCount="indefinite" />
          <animate attributeName="opacity" values="0.25;0.05;0.25" dur="2s" repeatCount="indefinite" />
        </circle>
        <circle cx={cx} cy={cy} r={4} fill="var(--background)" stroke="var(--primary)" strokeWidth={2} />
      </g>
    )
  }

  return (
    <div className="relative h-full w-full">
      {/* Botão de Reload com feedback de spin */}
      <button
        type="button"
        onClick={handleReload}
        disabled={recarregando}
        title="Atualizar histórico em segundo plano"
        className="absolute top-0 right-0 z-10 flex items-center justify-center h-7 w-7 rounded-full border border-border/60 bg-card text-muted-foreground hover:text-primary hover:border-primary/40 transition-all disabled:opacity-80 disabled:cursor-not-allowed"
      >
        <RefreshCw className={`w-3.5 h-3.5 ${recarregando ? 'animate-spin text-primary' : ''}`} />
      </button>

      {erroReload && (
        <span className="absolute top-9 right-0 z-10 text-[10px] text-red-500 font-medium max-w-[160px] text-right">
          {erroReload}
        </span>
      )}

      {/* Overlay de carregamento discreto apenas sobre a área do gráfico */}
      {recarregando && dadosOrdenados.length === 0 && (
        <div className="absolute inset-0 z-20 flex flex-col items-center justify-center bg-background/50 backdrop-blur-sm rounded-xl">
          <Loader2 className="w-8 h-8 text-primary animate-spin mb-2" />
          <p className="text-xs text-muted-foreground animate-pulse font-medium">
            Montando histórico em segundo plano...
          </p>
        </div>
      )}

      {dadosOrdenados.length === 0 ? (
        <div className="h-full w-full flex flex-col items-center justify-center border border-dashed border-border rounded-xl bg-muted/10 p-4">
          <p className="text-xs text-muted-foreground text-center">
            Nenhum dado histórico encontrado.<br />Clique no botão acima para processar.
          </p>
        </div>
      ) : (
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={dadosOrdenados} margin={{ top: 12, right: 12, left: -12, bottom: 0 }}>
            <defs>
              <linearGradient id="chartGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="var(--primary)" stopOpacity={0.15} />
                <stop offset="100%" stopColor="var(--primary)" stopOpacity={0.0} />
              </linearGradient>
            </defs>
    
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
              domain={['dataMin - 500', 'dataMax + 500']}
            />
            
            <Tooltip
              cursor={{ stroke: 'var(--border)', strokeWidth: 1, strokeDasharray: '4 4' }}
              content={({ active, payload }) => {
                if (active && payload && payload.length) {
                  const currentData = payload[0].payload
                  if (!currentData.date) return null
                  
                  const [ano, mes] = currentData.date.split('T')[0].split('-')
                  const dataTooltip = new Date(Number(ano), Number(mes) - 1, 1)
                  const ehHoje = isHoje(currentData.date)
    
                  const patrimonio = currentData.value || 0
                  const investido = currentData.investido || patrimonio
                  const lucro = currentData.lucro !== undefined ? currentData.lucro : (patrimonio - investido)
    
                  return (
                    <div className="bg-popover border border-border/80 rounded-lg shadow-md p-3 transition-all backdrop-blur-sm min-w-[180px]">
                      <div className="flex items-center justify-between gap-2 mb-2 border-b border-border/60 pb-1">
                        <p className="text-[10px] uppercase font-bold tracking-wider text-muted-foreground">
                          {ehHoje
                            ? 'Hoje'
                            : new Intl.DateTimeFormat('pt-BR', {
                                month: 'long',
                                year: 'numeric'
                              }).format(dataTooltip)}
                        </p>
                        {ehHoje && (
                          <span className="flex items-center gap-1 text-[9px] font-semibold text-primary uppercase tracking-wide">
                            <span className="relative flex h-1.5 w-1.5">
                              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary opacity-75" />
                              <span className="relative inline-flex rounded-full h-1.5 w-1.5 bg-primary" />
                            </span>
                            Ao vivo
                          </span>
                        )}
                      </div>
                      
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
            
            <Area
              type="monotone"
              dataKey="value"
              stroke="var(--primary)"
              strokeWidth={2}
              dot={renderDot}
              activeDot={{ r: 5, stroke: 'var(--background)', strokeWidth: 2 }}
              fill="url(#chartGradient)"
              connectNulls={true}
            />
          </AreaChart>
        </ResponsiveContainer>
      )}
    </div>
  )
}
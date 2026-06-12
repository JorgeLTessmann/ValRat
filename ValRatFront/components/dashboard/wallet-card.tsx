'use client'

import { useState } from 'react'
import { Eye, EyeOff, TrendingUp, TrendingDown } from 'lucide-react'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import { cn } from '@/lib/utils'
import { PortfolioChart } from './portfolio-chart'

interface WalletCardProps {
  totalBalance: number
  profitLoss: number
  percentChange: number
  historicalData: { date: string; value: number }[]
  isLoading?: boolean
}

export function WalletCard({
  totalBalance,
  profitLoss,
  percentChange,
  historicalData,
  isLoading
}: WalletCardProps) {
  const [isVisible, setIsVisible] = useState(true)
  const [timeframe, setTimeframe] = useState<'1D' | '1W' | '1M' | '1Y' | 'ALL'>('1M')

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value)
  }

  const isPositive = profitLoss >= 0

  const getFilteredData = () => {
    if (!historicalData.length) return []
    
    const now = new Date()
    let startDate: Date

    switch (timeframe) {
      case '1D':
        startDate = new Date(now)
        startDate.setDate(startDate.getDate() - 1)
        break
      case '1W':
        startDate = new Date(now)
        startDate.setDate(startDate.getDate() - 7)
        break
      case '1M':
        startDate = new Date(now)
        startDate.setMonth(startDate.getMonth() - 1)
        break
      case '1Y':
        startDate = new Date(now)
        startDate.setFullYear(startDate.getFullYear() - 1)
        break
      default:
        return historicalData
    }

    return historicalData.filter(item => new Date(item.date) >= startDate)
  }

  if (isLoading) {
    return (
      <Card className="overflow-hidden border-border/60 shadow-sm">
        <CardContent className="p-6 lg:p-8">
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <Skeleton className="h-4 w-32" />
              <Skeleton className="h-8 w-8 rounded-md" />
            </div>
            <Skeleton className="h-12 w-3/4 max-w-[280px]" />
            <div className="flex gap-3">
              <Skeleton className="h-6 w-20 rounded-full" />
              <Skeleton className="h-6 w-24" />
            </div>
            <div className="flex gap-1">
              {[1, 2, 3, 4, 5].map((i) => (
                <Skeleton key={i} className="h-8 w-10" />
              ))}
            </div>
            <Skeleton className="h-[200px] w-full rounded-xl" />
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="overflow-hidden border-border/60 shadow-sm bg-card transition-all duration-200">
      <CardContent className="p-6 lg:p-8">
        <div className="flex items-center justify-between mb-1.5">
          <span className="text-xs font-bold text-muted-foreground uppercase tracking-wider">
            Patrimônio Total
          </span>
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8 text-muted-foreground hover:text-foreground hover:bg-muted transition-colors"
            onClick={() => setIsVisible(!isVisible)}
            title={isVisible ? "Ocultar valores" : "Mostrar valores"}
          >
            {isVisible ? <Eye className="h-4 w-4" /> : <EyeOff className="h-4 w-4" />}
          </Button>
        </div>

        <div className="mb-3">
          <h2 className="text-3xl lg:text-4xl font-bold tracking-tight text-foreground font-mono">
            {isVisible ? formatCurrency(totalBalance) : '••••••••'}
          </h2>
        </div>

        <div className="flex items-center gap-2.5 mb-8">
          <div className={cn(
            'flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-semibold border shadow-none',
            isPositive 
              ? 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/20' 
              : 'bg-rose-500/10 text-rose-600 dark:text-rose-400 border-rose-500/20'
          )}>
            {isPositive ? (
              <TrendingUp className="h-3 w-3 shrink-0" />
            ) : (
              <TrendingDown className="h-3 w-3 shrink-0" />
            )}
            <span>{isVisible ? `${isPositive ? '+' : ''}${percentChange.toFixed(2)}%` : '••••'}</span>
          </div>
          
          <span className={cn(
            'text-sm font-semibold font-mono',
            isPositive ? 'text-emerald-600 dark:text-emerald-400' : 'text-rose-600 dark:text-rose-400'
          )}>
            {isVisible ? `${isPositive ? '+' : ''}${formatCurrency(profitLoss)}` : '••••••'}
          </span>
        </div>

        {/* Container de Períodos Refatorado estilo ToggleGroup */}
        <div className="flex gap-1 mb-6 bg-muted/50 p-1 rounded-lg w-fit border border-border/40">
          {(['1D', '1W', '1M', '1Y', 'ALL'] as const).map((tf) => (
            <Button
              key={tf}
              variant="ghost"
              size="sm"
              className={cn(
                'text-xs px-3 h-7 font-medium rounded-md transition-all duration-150 shadow-none',
                timeframe === tf 
                  ? 'bg-background text-foreground shadow-sm border border-border/40' 
                  : 'text-muted-foreground hover:text-foreground hover:bg-transparent'
              )}
              onClick={() => setTimeframe(tf)}
            >
              {tf}
            </Button>
          ))}
        </div>

        <div className="h-[180px] lg:h-[220px] w-full">
          <PortfolioChart data={getFilteredData()} isVisible={isVisible} />
        </div>
      </CardContent>
    </Card>
  )
}
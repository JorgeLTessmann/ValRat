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
      <Card className="overflow-hidden border-border/50 shadow-sm">
        <CardContent className="p-8">
          <div className="space-y-6">
            <Skeleton className="h-6 w-32" />
            <Skeleton className="h-14 w-64" />
            <Skeleton className="h-6 w-48" />
            <Skeleton className="h-[200px] w-full" />
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="overflow-hidden border-border/50 shadow-sm hover:shadow-md transition-shadow duration-300">
      <CardContent className="p-6 lg:p-8">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-muted-foreground uppercase tracking-wide">
            Patrimônio Total
          </span>
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8 text-primary hover:text-primary/80 hover:bg-accent"
            onClick={() => setIsVisible(!isVisible)}
          >
            {isVisible ? <Eye className="h-4 w-4" /> : <EyeOff className="h-4 w-4" />}
          </Button>
        </div>

        <div className="mb-4">
          <h2 className="text-4xl lg:text-5xl font-bold tracking-tight text-foreground">
            {isVisible ? formatCurrency(totalBalance) : '••••••••'}
          </h2>
        </div>

        <div className="flex items-center gap-3 mb-8">
          <div className={cn(
            'flex items-center gap-1 px-2.5 py-1 rounded-full text-sm font-medium',
            isPositive 
              ? 'bg-emerald-50 text-emerald-700' 
              : 'bg-red-50 text-red-700'
          )}>
            {isPositive ? (
              <TrendingUp className="h-3.5 w-3.5" />
            ) : (
              <TrendingDown className="h-3.5 w-3.5" />
            )}
            <span>{isVisible ? `${isPositive ? '+' : ''}${percentChange.toFixed(2)}%` : '••••'}</span>
          </div>
          <span className={cn(
            'text-sm font-medium',
            isPositive ? 'text-emerald-700' : 'text-red-700'
          )}>
            {isVisible ? `${isPositive ? '+' : ''}${formatCurrency(profitLoss)}` : '••••••'}
          </span>
        </div>

        <div className="flex gap-1 mb-6">
          {(['1D', '1W', '1M', '1Y', 'ALL'] as const).map((tf) => (
            <Button
              key={tf}
              variant={timeframe === tf ? 'default' : 'ghost'}
              size="sm"
              className={cn(
                'text-xs px-3 h-8 transition-all duration-200',
                timeframe === tf 
                  ? 'bg-primary text-primary-foreground shadow-sm' 
                  : 'text-muted-foreground hover:text-foreground hover:bg-accent'
              )}
              onClick={() => setTimeframe(tf)}
            >
              {tf}
            </Button>
          ))}
        </div>

        <div className="h-[180px] lg:h-[220px]">
          <PortfolioChart data={getFilteredData()} isVisible={isVisible} />
        </div>
      </CardContent>
    </Card>
  )
}

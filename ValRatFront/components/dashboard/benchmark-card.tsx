'use client'

import { TrendingUp, TrendingDown, Minus } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { cn } from '@/lib/utils'

interface BenchmarkProps {
  carteira: number
  cdi: number
  selic: number
  ibov: number
  isLoading?: boolean
}

export function BenchmarkCard({
  carteira,
  cdi,
  selic,
  ibov,
  isLoading
}: BenchmarkProps) {
  
  const benchmarks = [
    {
      label: 'Sua Carteira',
      value: carteira,
      isMain: true
    },
    {
      label: 'CDI',
      value: cdi,
      isMain: false
    },
    {
      label: 'SELIC',
      value: selic,
      isMain: false
    },
    {
      label: 'Ibovespa',
      value: ibov,
      isMain: false
    }
  ]

  const formatPercent = (val: number) => {
    return `${val >= 0 ? '+' : ''}${val.toFixed(2)}%`
  }

  if (isLoading) {
    return (
      <Card className="border-border/60 shadow-sm">
        <CardHeader className="pb-3">
          <Skeleton className="h-5 w-28" />
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="space-y-2">
                <div className="flex justify-between">
                  <Skeleton className="h-4 w-16" />
                  <Skeleton className="h-4 w-12" />
                </div>
                <Skeleton className="h-1.5 w-full rounded-full" />
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="border-border/60 shadow-sm bg-card relative before:absolute before:inset-x-0 before:top-0 before:h-[2px] before:bg-gradient-to-r before:from-transparent before:via-[#D4AF37]/30 before:to-transparent">
      <CardHeader className="pb-3">
        <CardTitle className="text-xs font-bold text-muted-foreground uppercase tracking-wider">
          Rentabilidade vs Benchmarks
        </CardTitle>
      </CardHeader>
      
      <CardContent>
        <div className="space-y-3">
          {benchmarks.map((item) => {
            const isPositive = item.value >= 0
            const isZero = item.value === 0

            return (
              <div 
                key={item.label}
                className={cn(
                  "p-2.5 rounded-lg border transition-colors",
                  item.isMain 
                    ? "bg-amber-500/[0.02] border-amber-500/10 shadow-sm" 
                    : "bg-transparent border-transparent hover:bg-muted/40"
                )}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className={cn(
                    "text-sm tracking-tight",
                    item.isMain 
                      ? "font-bold text-foreground" 
                      : "font-medium text-muted-foreground"
                  )}>
                    {item.label}
                  </span>
                  
                  <div className="flex items-center gap-1.5">
                    {isZero ? (
                      <Minus className="h-3 w-3 text-muted-foreground" />
                    ) : isPositive ? (
                      <TrendingUp className="h-3 w-3 text-emerald-500 dark:text-emerald-400" />
                    ) : (
                      <TrendingDown className="h-3 w-3 text-rose-500 dark:text-rose-400" />
                    )}
                    
                    {/* Apenas o valor em formato quadrado (mono) */}
                    <span className={cn(
                      "font-mono tracking-tight font-bold",
                      isZero 
                        ? "text-muted-foreground"
                        : isPositive 
                          ? "text-emerald-600 dark:text-emerald-400" 
                          : "text-rose-600 dark:text-rose-400",
                      item.isMain ? "text-base text-[#D4AF37]" : "text-sm"
                    )}>
                      {formatPercent(item.value)}
                    </span>
                  </div>
                </div>

                {/* Barra interna com o detalhe em ouro para a carteira principal */}
                <div className="w-full bg-muted h-1 rounded-full overflow-hidden">
                  <div 
                    className={cn(
                      "h-full rounded-full transition-all duration-500",
                      item.isMain 
                        ? "bg-[#D4AF37]" 
                        : isPositive 
                          ? "bg-emerald-500/50" 
                          : "bg-rose-500/50"
                    )}
                    style={{ width: `${Math.min(Math.max(Math.abs(item.value) * 4, 2), 100)}%` }}
                  />
                </div>
              </div>
            )
          })}
        </div>
      </CardContent>
    </Card>
  )
}
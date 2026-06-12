'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { cn } from '@/lib/utils'
import type { PortfolioAllocation } from '@/lib/types'
import { assetTypeLabels } from '@/lib/types'

interface AssetAllocationProps {
  allocations: PortfolioAllocation[]
  isLoading?: boolean
}

export function AssetAllocation({ allocations, isLoading }: AssetAllocationProps) {
  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value)
  }

  if (isLoading) {
    return (
      <Card className="border-border/60 shadow-sm">
        <CardHeader className="pb-4">
          <Skeleton className="h-5 w-40" />
        </CardHeader>
        <CardContent className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="p-4 border border-border/40 rounded-xl space-y-3">
              <div className="flex justify-between">
                <Skeleton className="h-4 w-24" />
                <Skeleton className="h-4 w-12" />
              </div>
              <Skeleton className="h-2 w-full rounded-full" />
            </div>
          ))}
        </CardContent>
      </Card>
    )
  }

  const getTypeColor = (index: number) => {
    const colors = [
      'bg-[#D4AF37]', // Primeiro item/maior alocação em Dourado Ouro
      'bg-indigo-500 dark:bg-indigo-400',
      'bg-emerald-500 dark:bg-emerald-400',
      'bg-amber-500 dark:bg-amber-400',
      'bg-violet-500 dark:bg-violet-400'
    ]
    return colors[index % colors.length]
  }

  return (
    <Card className="border-border/60 shadow-sm bg-card">
      <CardHeader className="pb-3">
        <CardTitle className="text-xs font-bold text-muted-foreground uppercase tracking-wider">
          Alocação por Classe
        </CardTitle>
      </CardHeader>
      
      <CardContent className="space-y-3">
        {allocations.map((allocation, index) => (
          <div
            key={allocation.type}
            className={cn(
              "p-4 rounded-xl border transition-all duration-200",
              index === 0 
                ? "bg-amber-500/[0.02] border-amber-500/20 hover:bg-amber-500/[0.04]" 
                : "bg-muted/30 border-border/40 hover:bg-muted/60"
            )}
          >
            <div className="flex items-center justify-between mb-2.5">
              <div className="flex items-center gap-2.5">
                <div
                  className={cn(
                    'w-2.5 h-2.5 rounded-full ring-2 ring-background shrink-0',
                    getTypeColor(index)
                  )}
                />
                {/* Texto em fonte normal do sistema */}
                <span className="text-sm font-semibold tracking-tight text-foreground">
                  {assetTypeLabels[allocation.type] || allocation.type}
                </span>
              </div>
              {/* Apenas a porcentagem em formato quadrado (mono) */}
              <span className={cn("text-sm font-bold font-mono", index === 0 ? "text-[#D4AF37]" : "text-foreground")}>
                {allocation.percentage.toFixed(1)}%
              </span>
            </div>
            
            {/* Barra de Progresso */}
            <div className="relative h-1.5 w-full bg-muted rounded-full overflow-hidden mb-2.5">
              <div
                className={cn('absolute inset-y-0 left-0 rounded-full transition-all duration-500 ease-out', getTypeColor(index))}
                style={{ width: `${allocation.percentage}%` }}
              />
            </div>
            
            {/* Textos em fonte normal, apenas os números finais em mono */}
            <div className="flex justify-between text-xs text-muted-foreground font-medium">
              <span>
                Investido: <span className="font-mono text-foreground/80 font-semibold">{formatCurrency(allocation.totalInvested)}</span>
              </span>
              <span>
                Atual: <span className="font-mono text-foreground/80 font-semibold">{formatCurrency(allocation.currentValue)}</span>
              </span>
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  )
}
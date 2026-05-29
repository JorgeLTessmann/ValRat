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
      <Card className="border-border/50 shadow-sm">
        <CardHeader className="pb-4">
          <Skeleton className="h-6 w-40" />
        </CardHeader>
        <CardContent className="space-y-4">
          {[1, 2, 3, 4, 5].map((i) => (
            <Skeleton key={i} className="h-16 w-full" />
          ))}
        </CardContent>
      </Card>
    )
  }

  const getTypeColor = (index: number) => {
    const colors = [
      'bg-[#D4AF37]', // Primary Gold
      'bg-[#8A6D3B]', // Dark Gold
      'bg-[#F3E5AB]', // Champagne
      'bg-emerald-500', // Success
      'bg-[#6B7280]'  // Muted
    ]
    return colors[index % colors.length]
  }

  return (
    <Card className="border-border/50 shadow-sm hover:shadow-md transition-shadow duration-300">
      <CardHeader className="pb-4">
        <CardTitle className="text-lg font-semibold text-accent-foreground">
          Alocação por Classe
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {allocations.map((allocation, index) => (
          <div
            key={allocation.type}
            className="group p-4 rounded-xl bg-secondary/30 hover:bg-secondary/50 transition-colors duration-200"
          >
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-3">
                <div
                  className={cn(
                    'w-3 h-3 rounded-full',
                    getTypeColor(index)
                  )}
                />
                <span className="font-medium text-foreground">
                  {assetTypeLabels[allocation.type]}
                </span>
              </div>
              <span className="text-sm font-semibold text-foreground">
                {allocation.percentage.toFixed(1)}%
              </span>
            </div>
            
            <div className="relative h-2 bg-border rounded-full overflow-hidden mb-3">
              <div
                className={cn(
                  'absolute inset-y-0 left-0 rounded-full transition-all duration-500 ease-out',
                  getTypeColor(index)
                )}
                style={{ width: `${allocation.percentage}%` }}
              />
            </div>
            
            <div className="flex justify-between text-xs text-muted-foreground">
              <span>Investido: {formatCurrency(allocation.totalInvested)}</span>
              <span>Atual: {formatCurrency(allocation.currentValue)}</span>
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  )
}

'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { cn } from '@/lib/utils'

interface ClasseAlocacao {
  label: string
  value: number // Percentual de 0 a 100
}

interface AlocacaoClasseProps {
  classes: ClasseAlocacao[]
  isLoading?: boolean
}

export function AlocacaoClasseCard({ classes, isLoading }: AlocacaoClasseProps) {
  if (isLoading) {
    return (
      <Card className="border-border/60 shadow-sm">
        <CardHeader className="pb-3">
          <Skeleton className="h-5 w-36" />
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="space-y-2">
                <div className="flex justify-between">
                  <Skeleton className="h-4 w-24" />
                  <Skeleton className="h-4 w-10" />
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
          Alocação por Classe de Ativos
        </CardTitle>
      </CardHeader>
      
      <CardContent>
        <div className="space-y-4">
          {classes.map((item) => {
            const percentual = Math.min(Math.max(item.value, 0), 100)

            return (
              <div key={item.label} className="space-y-2 p-1">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-muted-foreground tracking-tight">
                    {item.label}
                  </span>
                  
                  <span className="font-mono text-sm font-bold text-foreground">
                    {percentual.toFixed(2)}%
                  </span>
                </div>

                {/* Barra preenchida de acordo com o percentual real da classe */}
                <div className="w-full bg-muted h-1.5 rounded-full overflow-hidden">
                  <div 
                    className="h-full rounded-full bg-[#D4AF37] transition-all duration-500"
                    style={{ width: `${percentual}%` }}
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
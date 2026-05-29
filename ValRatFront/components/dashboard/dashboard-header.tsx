'use client'

import { Card, CardContent } from '@/components/ui/card'
import { cn } from '@/lib/utils'

interface DashboardHeaderProps {
  userName?: string
}

export function DashboardHeader({ userName = 'Investidor' }: DashboardHeaderProps) {
  const getGreeting = () => {
    const hour = new Date().getHours()
    if (hour < 12) return 'Bom dia'
    if (hour < 18) return 'Boa tarde'
    return 'Boa noite'
  }

  return (
    <div className="mb-8">
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <div className="flex items-center gap-2">
              <span className="text-2xl font-bold tracking-tight text-primary">Val</span>
              <span className="text-2xl font-bold tracking-tight text-foreground">Rat</span>
            </div>
          </div>
          <h1 className="text-3xl lg:text-4xl font-bold text-foreground tracking-tight">
            {getGreeting()}, <span className="text-accent-foreground">{userName}</span>
          </h1>
          <p className="mt-1 text-muted-foreground">
            Acompanhe seu portfólio e tome decisões mais inteligentes.
          </p>
        </div>
        
        <div className="hidden md:flex items-center gap-4">
          <Card className="border-border/50 shadow-sm">
            <CardContent className="py-2 px-4">
              <div className="flex items-center gap-2">
                <div className={cn(
                  'w-2 h-2 rounded-full animate-pulse',
                  'bg-emerald-500'
                )} />
                <span className="text-xs text-muted-foreground">Mercado Aberto</span>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}

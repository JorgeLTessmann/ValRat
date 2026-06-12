'use client'

import { useEffect, useState } from 'react'
import { Card, CardContent } from '@/components/ui/card'
import { cn } from '@/lib/utils'

interface DashboardHeaderProps {
  userName?: string
}

export function DashboardHeader({ userName = 'Investidor' }: DashboardHeaderProps) {
  const [marketStatus, setMarketStatus] = useState<{ label: string; isOpen: boolean }>({
    label: 'Verificando...',
    isOpen: false
  })

  const getGreeting = () => {
    const hour = new Date().getHours()
    if (hour < 12) return 'Bom dia'
    if (hour < 18) return 'Boa tarde'
    return 'Boa noite'
  }

  // Lógica dinâmica para verificar o status de funcionamento da B3 (Seg a Sex, 10h às 17h55)
  useEffect(() => {
    const checkMarketStatus = () => {
      const now = new Date()
      const day = now.getDay() // 0 = Domingo, 6 = Sábado
      const hour = now.getHours()
      const minutes = now.getMinutes()
      const timeAsDecimal = hour + minutes / 60

      if (day === 0 || day === 6) {
        setMarketStatus({ label: 'Mercado Fechado (Fim de semana)', isOpen: false })
      } else if (timeAsDecimal >= 10 && timeAsDecimal < 17.91) { // ~17h55
        setMarketStatus({ label: 'Mercado Aberto', isOpen: true })
      } else {
        setMarketStatus({ label: 'Mercado Fechado', isOpen: false })
      }
    }

    checkMarketStatus()
    const interval = setInterval(checkMarketStatus, 60000) // Atualiza a cada 1 minuto
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="mb-8">
      <div className="flex items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-1 mb-1.5 select-none">
            <span className="text-xl font-black tracking-tight text-primary">Val</span>
            <span className="text-xl font-black tracking-tight text-foreground">Rat</span>
          </div>
          
          <h1 className="text-3xl lg:text-4xl font-bold text-foreground tracking-tight">
            {getGreeting()}, <span className="text-primary font-extrabold">{userName}</span>
          </h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Acompanhe seu portfólio e tome decisões mais inteligentes.
          </p>
        </div>
        
        {/* Indicador de Mercado Dinâmico */}
        <div className="hidden md:block shrink-0">
          <Card className="border-border/60 shadow-sm bg-card">
            <CardContent className="py-2 px-3.5">
              <div className="flex items-center gap-2.5">
                <span className="relative flex h-2 w-2">
                  {marketStatus.isOpen && (
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                  )}
                  <span className={cn(
                    "relative inline-flex rounded-full h-2 w-2",
                    marketStatus.isOpen 
                      ? "bg-emerald-500" 
                      : "bg-muted-foreground/50"
                  )} />
                </span>
                
                <span className="text-xs font-semibold tracking-wide text-muted-foreground font-mono">
                  {marketStatus.label}
                </span>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
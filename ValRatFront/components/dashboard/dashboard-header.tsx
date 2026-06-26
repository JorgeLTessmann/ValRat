'use client'

import { useEffect, useState } from 'react'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import { useAuth } from '@/hooks/use-auth'
import { LogOut, User, Users, Boxes } from 'lucide-react'
import { InventarioModal } from '@/components/dashboard/inventario-modal'

interface DashboardHeaderProps {
  userName?: string
}

export function DashboardHeader({ userName = 'Investidor' }: DashboardHeaderProps) {
  const { currentUser, logoutCurrent } = useAuth()

  const [marketStatus, setMarketStatus] = useState<{ label: string; isOpen: boolean }>({
    label: 'Verificando...',
    isOpen: false
  })

  const [inventarioOpen, setInventarioOpen] = useState(false)

  const getGreeting = () => {
    const hour = new Date().getHours()
    if (hour < 12) return 'Bom dia'
    if (hour < 18) return 'Boa tarde'
    return 'Boa noite'
  }

  useEffect(() => {
    const userEmail = currentUser?.email || (typeof currentUser === 'string' ? currentUser : null)

    if (!userEmail) return

    const sincronizarHistoricoBackend = async () => {
      try {

        const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'https://valrat.onrender.com'

        const response = await fetch(`${baseUrl}/historico/sincronizar`, {
          method: 'GET',
          headers: {
            'X-User-Email': userEmail
          }
        })

        if (!response.ok) {
          console.warn(`[HISTÓRICO] Sincronização retornou status ${response.status}`)
          return
        }

        console.log('[HISTÓRICO] Comando de sincronização inteligente enviado ao backend.')
      } catch (error) {

        console.error('[HISTÓRICO ERRO] Falha ao acionar sincronização automática:', error)
      }
    }

    sincronizarHistoricoBackend()
  }, [currentUser])

  useEffect(() => {
    const checkMarketStatus = () => {
      const now = new Date()
      const day = now.getDay()
      const hour = now.getHours()
      const minutes = now.getMinutes()
      const timeAsDecimal = hour + minutes / 60

      if (day === 0 || day === 6) {
        setMarketStatus({ label: 'Mercado Fechado (Fim de semana)', isOpen: false })
      } else if (timeAsDecimal >= 10 && timeAsDecimal < 17.91) {
        setMarketStatus({ label: 'Mercado Aberto', isOpen: true })
      } else {
        setMarketStatus({ label: 'Mercado Fechado', isOpen: false })
      }
    }

    checkMarketStatus()
    const interval = setInterval(checkMarketStatus, 60000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="mb-8">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-1 mb-1.5 select-none">
            <span className="text-xl font-black tracking-tight text-primary">Val</span>
            <span className="text-xl font-black tracking-tight text-foreground">Rat</span>
          </div>

          <h1 className="text-3xl lg:text-4xl font-bold text-foreground tracking-tight">
            {getGreeting()}, <span className="text-primary font-extrabold">{userName}</span>
          </h1>
          <p className="mt-1 text-sm text-muted-foreground flex items-center gap-1.5">
            <User className="w-3.5 h-3.5 text-primary/70" />
            {currentUser?.email || 'Painel de Controle de Investimentos'}
          </p>
        </div>

        <div className="flex items-center gap-3 self-end md:self-auto shrink-0">
          <div className="hidden sm:block">
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

          <Button
            variant="outline"
            size="sm"
            onClick={() => setInventarioOpen(true)}
            className="h-9 gap-2 border-border/60 text-xs font-semibold shadow-sm hover:bg-secondary transition-all"
          >
            <Boxes className="w-4 h-4 text-primary/70" />
            <span className="hidden xs:inline">Inventário</span>
          </Button>

          <Button
            variant="outline"
            size="sm"
            onClick={logoutCurrent}
            className="h-9 gap-2 border-border/60 text-xs font-semibold shadow-sm hover:bg-secondary transition-all"
          >
            <Users className="w-4 h-4 text-muted-foreground" />
            <span className="hidden xs:inline">Alternar Perfil</span>
            <LogOut className="w-3.5 h-3.5 text-muted-foreground/70" />
          </Button>
        </div>
      </div>

      <InventarioModal open={inventarioOpen} onOpenChange={setInventarioOpen} />
    </div>
  )
}
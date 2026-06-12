'use client'

import { useState, useEffect } from 'react'
import useSWR from 'swr'
import {
  DashboardHeader,
  WalletCard,
  AssetAllocation,
  QuickActions,
  TransactionLedger,
  HoldingsTable,
  StatsGrid,
  EmptyState
} from '@/components/dashboard'
import {
  fetchPortfolioResumo,
  fetchPortfolioData,
  fetchHistorico,
  fetchBenchmarks
} from '@/lib/api'
import { CompraModal } from '@/components/dashboard/compra-modal'
import { RendimentoModal } from '@/components/dashboard/rendimento-modal'
import { RetiradaModal } from '@/components/dashboard/retirada-modal'
import { PatrimonioChart } from '@/components/dashboard/patrimonio-chart'
import { BenchmarkCard } from '@/components/dashboard/benchmark-card'
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle
} from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import {
  TrendingUp,
  Wallet,
  Landmark,
  PieChart,
  LogIn,
  Shield
} from 'lucide-react'

export default function DashboardPage() {
  // Estado de autenticação
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [isLoadingAuth, setIsLoadingAuth] = useState(false)

  const [openCompra, setOpenCompra] = useState(false)
  const [isRendimentoOpen, setIsRendimentoOpen] = useState(false)
  const [openRetirada, setOpenRetirada] = useState(false)

  // Dados rápidos (carregam primeiro)
  const [resumoData, setResumoData] = useState<any>(null)
  const [resumoLoading, setResumoLoading] = useState(true)

  // Dados completos (carregam depois)
  const { data: portfolio, isLoading: portfolioLoading, mutate } = useSWR(
    'portfolio-completo',
    fetchPortfolioData,
    {
      refreshInterval: 0,
      revalidateOnFocus: false,
      dedupingInterval: 30000
    }
  )

  const { data: historico } = useSWR(
    'historico',
    fetchHistorico,
    {
      refreshInterval: 0,
      revalidateOnFocus: false
    }
  )

  const { data: benchmarks } = useSWR(
    'benchmarks',
    fetchBenchmarks,
    {
      refreshInterval: 60000,
      revalidateOnFocus: false
    }
  )

  // Carrega dados rápidos primeiro
  useEffect(() => {
    const loadResumo = async () => {
      try {
        const data = await fetchPortfolioResumo()
        setResumoData(data)
      } catch (error) {
        console.error('Erro ao carregar resumo:', error)
        // Define dados padrão para não quebrar
        setResumoData({ totalBalance: 0, totalInvested: 0, profitLoss: 0, percentChange: 0 })
      } finally {
        setResumoLoading(false)
      }
    }
    loadResumo()
  }, [])

  // Tela de acesso
  const handleAcessarConta = () => {
    setIsLoadingAuth(true)
    setTimeout(() => {
      setIsAuthenticated(true)
      setIsLoadingAuth(false)
    }, 800)
  }

  // Se não autenticado
  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center space-y-6 max-w-md mx-auto px-4">
          <div className="flex justify-center">
            <div className="w-20 h-20 rounded-full bg-primary/10 flex items-center justify-center">
              <Shield className="w-10 h-10 text-primary" />
            </div>
          </div>
          <div>
            <h1 className="text-3xl font-bold text-foreground mb-2">ValRat</h1>
            <p className="text-muted-foreground">Seu gestor de investimentos pessoal</p>
          </div>
          <Card className="border-border/50 shadow-sm">
            <CardContent className="pt-6">
              <div className="space-y-4">
                <div className="text-left space-y-2">
                  <p className="text-sm text-muted-foreground">
                    Acesse sua conta para visualizar seus investimentos, acompanhar rentabilidade e gerenciar sua carteira.
                  </p>
                  <div className="bg-secondary/30 rounded-lg p-3">
                    <p className="text-xs text-muted-foreground">🔒 Ambiente seguro e criptografado</p>
                  </div>
                </div>
                <Button onClick={handleAcessarConta} disabled={isLoadingAuth} className="w-full gap-2" size="lg">
                  {isLoadingAuth ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                      Acessando...
                    </>
                  ) : (
                    <>
                      <LogIn className="w-4 h-4" />
                      Acessar Conta
                    </>
                  )}
                </Button>
              </div>
            </CardContent>
          </Card>
          <p className="text-xs text-muted-foreground">Versão de demonstração • Dados de mercado podem ter atraso</p>
        </div>
      </div>
    )
  }

  // Tela de loading (enquanto carrega)
  if (resumoLoading || portfolioLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center space-y-4">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <p className="text-muted-foreground">Carregando seus investimentos...</p>
        </div>
      </div>
    )
  }

  // Após carregar, verifica se há investimentos
  const temInvestimentos = portfolio?.assets && portfolio.assets.length > 0

  // Tela vazia (sem investimentos)
  if (!temInvestimentos) {
    return (
      <div className="min-h-screen bg-background">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <DashboardHeader userName="Pedro" />
          <div className="mb-8">
            <StatsGrid
              totalBalance={resumoData?.totalBalance ?? 0}
              totalInvested={resumoData?.totalInvested ?? 0}
              profitLoss={resumoData?.profitLoss ?? 0}
              percentChange={resumoData?.percentChange ?? 0}
              isLoading={false}
            />
          </div>
          <EmptyState onAddInvestment={() => setOpenCompra(true)} />
          <footer className="mt-12 pt-8 border-t border-border/50">
            <div className="flex flex-col sm:flex-row items-center justify-between gap-4 text-sm text-muted-foreground">
              <div className="flex items-center gap-2">
                <span className="font-bold text-primary">Val</span>
                <span className="font-bold text-foreground">Rat</span>
                <span>© 2026</span>
              </div>
              <p className="text-center sm:text-right">Dados de mercado podem ter atraso. Não é recomendação de investimento.</p>
            </div>
          </footer>
        </div>
        <CompraModal open={openCompra} onClose={() => setOpenCompra(false)} onSuccess={() => mutate()} />
      </div>
    )
  }

  // Dashboard completo
  return (
    <div className="min-h-screen bg-background">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <DashboardHeader userName="Pedro" />

        {/* Stats */}
        <div className="mb-8">
          <StatsGrid
            totalBalance={resumoData?.totalBalance ?? portfolio?.totalBalance ?? 0}
            totalInvested={resumoData?.totalInvested ?? portfolio?.totalInvested ?? 0}
            profitLoss={resumoData?.profitLoss ?? portfolio?.profitLoss ?? 0}
            percentChange={resumoData?.percentChange ?? portfolio?.percentChange ?? 0}
            isLoading={false}
          />
        </div>

        {/* Top grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          <div className="lg:col-span-2 space-y-6">
            <WalletCard
              totalBalance={portfolio?.totalBalance ?? resumoData?.totalBalance ?? 0}
              profitLoss={portfolio?.profitLoss ?? resumoData?.profitLoss ?? 0}
              percentChange={portfolio?.percentChange ?? resumoData?.percentChange ?? 0}
              historicalData={portfolio?.historicalData ?? []}
              isLoading={false}
            />
            <PatrimonioChart historico={historico ?? []} />
          </div>

          <div className="lg:col-span-1 space-y-6">
            <QuickActions
              onComprarClick={() => setOpenCompra(true)}
              onSimularRendimentoClick={() => setIsRendimentoOpen(true)}
              onVenderClick={() => setOpenRetirada(true)}
            />

            <Card className="border-border/50 shadow-sm">
              <CardHeader>
                <CardTitle>Resumo Geral</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-5">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <Wallet className="w-5 h-5 text-primary" />
                      <span>Patrimônio</span>
                    </div>
                    <span className="font-semibold">
                      {new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(portfolio?.totalBalance ?? resumoData?.totalBalance ?? 0)}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <Landmark className="w-5 h-5 text-primary" />
                      <span>Investido</span>
                    </div>
                    <span className="font-semibold">
                      {new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(portfolio?.totalInvested ?? resumoData?.totalInvested ?? 0)}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <TrendingUp className="w-5 h-5 text-primary" />
                      <span>Lucro</span>
                    </div>
                    <span className={`font-semibold ${(portfolio?.profitLoss ?? resumoData?.profitLoss ?? 0) >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                      {new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(portfolio?.profitLoss ?? resumoData?.profitLoss ?? 0)}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <PieChart className="w-5 h-5 text-primary" />
                      <span>Ativos</span>
                    </div>
                    <span className="font-semibold">{portfolio?.assets?.length ?? 0}</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Second grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          <div className="lg:col-span-1 space-y-6">
            <AssetAllocation allocations={portfolio?.allocations ?? []} isLoading={false} />
            <BenchmarkCard
              carteira={benchmarks?.carteira ?? 0}
              cdi={benchmarks?.cdi ?? 0}
              selic={benchmarks?.selic ?? 0}
              ibov={benchmarks?.ibov ?? 0}
            />
          </div>
          <div className="lg:col-span-2">
            <TransactionLedger transactions={portfolio?.transactions ?? []} isLoading={false} />
          </div>
        </div>

        {/* Holdings */}
        <div className="mb-8">
          <HoldingsTable assets={portfolio?.assets ?? []} isLoading={false} />
        </div>

        <footer className="mt-12 pt-8 border-t border-border/50">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4 text-sm text-muted-foreground">
            <div className="flex items-center gap-2">
              <span className="font-bold text-primary">Val</span>
              <span className="font-bold text-foreground">Rat</span>
              <span>© 2026</span>
            </div>
            <p className="text-center sm:text-right">Dados de mercado podem ter atraso. Não é recomendação de investimento.</p>
          </div>
        </footer>
      </div>

      <CompraModal open={openCompra} onClose={() => setOpenCompra(false)} onSuccess={() => mutate()} />
      <RendimentoModal open={isRendimentoOpen} onOpenChange={setIsRendimentoOpen} />
      <RetiradaModal
        open={openRetirada}
        onClose={() => setOpenRetirada(false)}
        onSuccess={() => mutate()}
        assets={portfolio?.assets ?? []}
      />
    </div>
  )
}
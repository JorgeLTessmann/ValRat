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
  fetchBenchmarks,
  loginUsuario,
  cadastrarUsuario
} from '@/lib/api'
import { CompraModal } from '@/components/dashboard/compra-modal'
import { RendimentoModal } from '@/components/dashboard/rendimento-modal'
import { RetiradaModal } from '@/components/dashboard/retirada-modal'
import { AlocacaoClasseCard } from '@/components/dashboard/benchmark-card'
import { useAuth } from '@/hooks/use-auth'
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
  Shield,
  User,
  X
} from 'lucide-react'

export default function DashboardPage() {
  // Desestruturação do hook com gerenciamento de perfis
  const {
    isAuthenticated,
    currentUser,
    savedProfiles,
    login,
    switchProfile,
    removeProfile
  } = useAuth()

  const userName = currentUser?.nome || 'Usuário'

  const [isLoadingAuth, setIsLoadingAuth] = useState(false)
  const [openCompra, setOpenCompra] = useState(false)
  const [isRendimentoOpen, setIsRendimentoOpen] = useState(false)
  const [openRetirada, setOpenRetirada] = useState(false)

  const [resumoData, setResumoData] = useState<any>(null)
  const [resumoLoading, setResumoLoading] = useState(true)

  // =========================================================================
  // HOOKS SWR: PASSANDO A URL CORRETA E O E-MAIL COMO ARGUMENTOS
  // =========================================================================

  const { data: portfolio, isLoading: portfolioLoading, mutate } = useSWR(
    isAuthenticated && currentUser?.email ? ['/carteira/completa', currentUser.email] : null,
    ([url, email]) => fetchPortfolioData(url, email),
    {
      refreshInterval: 0,
      revalidateOnFocus: false,
      dedupingInterval: 30000
    }
  )

  const { data: historico } = useSWR(
    isAuthenticated && currentUser?.email ? ['/historico', currentUser.email] : null,
    ([url, email]) => fetchHistorico(url, email),
    {
      refreshInterval: 0,
      revalidateOnFocus: false
    }
  )

  const { data: benchmarks } = useSWR(
    isAuthenticated && currentUser?.email ? ['/benchmark', currentUser.email] : null,
    ([url, email]) => fetchBenchmarks(url, email),
    {
      refreshInterval: 60000,
      revalidateOnFocus: false
    }
  )

  useEffect(() => {
    if (!isAuthenticated || !currentUser || !currentUser.email) return;

    const loadResumo = async () => {
      setResumoLoading(true);
      try {
        const data = await fetchPortfolioResumo('/carteira/rapida', currentUser.email);
        setResumoData(data);
      } catch (error) {
        console.error('Erro ao carregar resumo:', error);
      } finally {
        setResumoLoading(false);
      }
    };

    loadResumo();
  }, [isAuthenticated, currentUser?.email]);

  const [isCadastro, setIsCadastro] = useState(false)
  const [authForm, setAuthForm] = useState({ nome: '', email: '', senha: '' })
  const [authError, setAuthError] = useState('')

  const handleAuthSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoadingAuth(true)
    setAuthError('')

    try {
      if (isCadastro) {
        await cadastrarUsuario({ nome: authForm.nome, email: authForm.email, senha: authForm.senha })
        setIsCadastro(false)
        setAuthForm(prev => ({ ...prev, senha: '' }))
        alert("Cadastro realizado com sucesso! Faça o login.")
      } else {
        const usuario = await loginUsuario({ email: authForm.email, senha: authForm.senha })
        login(usuario.nome, authForm.email)
      }
    } catch (error: any) {
      setAuthError(error.message || 'Erro na autenticação.')
    } finally {
      setIsLoadingAuth(false)
    }
  }

  // Interface de Autenticação / Seletor de Perfis
  if (!isAuthenticated) {
    // Dashboard Completa Ativa
    return (
      <div className="min-h-screen bg-background">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 flex flex-col min-h-screen">

          <DashboardHeader userName={userName} />

          <div className="mb-8">
            <StatsGrid
              totalBalance={resumoData?.totalBalance ?? portfolio?.totalBalance ?? 0}
              totalInvested={resumoData?.totalInvested ?? portfolio?.totalInvested ?? 0}
              profitLoss={resumoData?.profitLoss ?? portfolio?.profitLoss ?? 0}
              percentChange={resumoData?.percentChange ?? portfolio?.percentChange ?? 0}
              isLoading={false}
            />
          </div>

          {/* PRIMEIRA SEÇÃO: Gráfico + Ações Rápidas e Resumo */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
            <div className="lg:col-span-2 space-y-6">
              <WalletCard
                totalBalance={portfolio?.totalBalance ?? resumoData?.totalBalance ?? 0}
                profitLoss={portfolio?.profitLoss ?? resumoData?.profitLoss ?? 0}
                percentChange={portfolio?.percentChange ?? resumoData?.percentChange ?? 0}
                historicalData={portfolio?.historicalData ?? []}
                isLoading={false}
              />
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

          {/* SEGUNDA SEÇÃO: Alocação por Classe de Ativos e Histórico de Transações lado a lado */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
            <div className="lg:col-span-1 space-y-6">
              <AssetAllocation allocations={portfolio?.allocations ?? []} isLoading={false} />
              <AlocacaoClasseCard
                isLoading={portfolioLoading}
                classes={
                  portfolio?.allocations?.map((alloc: any) => ({
                    label: alloc.classe || alloc.name || alloc.label,
                    value: alloc.percentual || alloc.percentage || alloc.value || 0
                  })) || []
                }
              />
            </div>
            <div className="lg:col-span-2">
              <TransactionLedger transactions={portfolio?.transactions ?? []} isLoading={false} />
            </div>
          </div>

          {/* TERCEIRA SEÇÃO: Tabela de Ativos ocupando a largura total isolada */}
          <div className="mb-8 w-full">
            <HoldingsTable assets={(portfolio?.assets ?? []) as any} />
          </div>

          {/* FOOTER: Empurrado para o final da página */}
          <footer className="mt-auto pt-8 border-t border-border/50 w-full">
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

        {/* Modais fora do fluxo do layout principal */}
        <CompraModal open={openCompra} onClose={() => setOpenCompra(false)} onSuccess={() => mutate()} />
        <RendimentoModal open={isRendimentoOpen} onOpenChange={setIsRendimentoOpen} />
        <RetiradaModal
          open={openRetirada}
          onClose={() => setOpenRetirada(false)}
          onSuccess={() => mutate()}
          assets={(portfolio?.assets ?? []) as any}
        />
      </div>
    )
  }

  // Estado de carregamento dos dados das rotas protegidas
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

  const temInvestimentos = portfolio?.assets && portfolio.assets.length > 0

  // View de Estado Vazio
  if (!temInvestimentos) {
    return (
      <div className="min-h-screen bg-background">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <DashboardHeader userName={userName} />
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
              <p className="text-center sm:text-right">Dados de mercado podem ter atraso. Não é recomendação de investmento.</p>
            </div>
          </footer>
        </div>
        <CompraModal open={openCompra} onClose={() => setOpenCompra(false)} onSuccess={() => mutate()} />
      </div>
    )
  }

  // Dashboard Completa Ativa
  return (
    <div className="min-h-screen bg-background">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <DashboardHeader userName={userName} />

        <div className="mb-8">
          <StatsGrid
            totalBalance={resumoData?.totalBalance ?? portfolio?.totalBalance ?? 0}
            totalInvested={resumoData?.totalInvested ?? portfolio?.totalInvested ?? 0}
            profitLoss={resumoData?.profitLoss ?? portfolio?.profitLoss ?? 0}
            percentChange={resumoData?.percentChange ?? portfolio?.percentChange ?? 0}
            isLoading={false}
          />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          <div className="lg:col-span-2 space-y-6">
            <WalletCard
              totalBalance={portfolio?.totalBalance ?? resumoData?.totalBalance ?? 0}
              profitLoss={portfolio?.profitLoss ?? resumoData?.profitLoss ?? 0}
              percentChange={portfolio?.percentChange ?? resumoData?.percentChange ?? 0}
              historicalData={portfolio?.historicalData ?? []}
              isLoading={false}
            />
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

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          <div className="lg:col-span-1 space-y-6">
            <AlocacaoClasseCard
              isLoading={portfolioLoading}
              classes={
                portfolio?.allocations?.map((alloc: any) => ({
                  label: alloc.classe || alloc.name || alloc.label, // Garante pegar a propriedade certa vinda do backend
                  value: alloc.percentual || alloc.percentage || alloc.value || 0
                })) || []
              }
            />
            <div className="lg:col-span-2">
              <TransactionLedger transactions={portfolio?.transactions ?? []} isLoading={false} />
            </div>
          </div>

          <div className="mb-8">
            <HoldingsTable assets={(portfolio?.assets ?? []) as any} />
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
          assets={(portfolio?.assets ?? []) as any}
        />
      </div>
    </div>
  )
}
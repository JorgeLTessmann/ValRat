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

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center py-12 px-4">
        <div className="text-center space-y-6 max-w-md mx-auto w-full">
          <div className="flex justify-center">
            <div className="w-20 h-20 rounded-full bg-primary/10 flex items-center justify-center">
              <Shield className="w-10 h-10 text-primary" />
            </div>
          </div>
          <div>
            <h1 className="text-3xl font-bold text-foreground mb-2">ValRat</h1>
            <p className="text-muted-foreground">Quem está investindo hoje?</p>
          </div>

          {savedProfiles.length > 0 && !isCadastro && (
            <div className="space-y-2 text-left">
              <label className="text-xs font-semibold text-muted-foreground px-1">Perfis salvos neste dispositivo</label>
              <div className="grid grid-cols-1 gap-2">
                {savedProfiles.map((perfil) => (
                  <div
                    key={perfil.email}
                    onClick={() => switchProfile(perfil.email)}
                    className="flex items-center justify-between p-3 bg-card border border-border/60 rounded-xl hover:border-primary/50 transition-all cursor-pointer group"
                  >
                    <div className="flex items-center gap-3 min-w-0">
                      <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center font-bold text-primary shrink-0">
                        {perfil.nome.charAt(0).toUpperCase()}
                      </div>
                      <div className="min-w-0">
                        <p className="font-medium text-sm text-foreground truncate">{perfil.nome}</p>
                        <p className="text-xs text-muted-foreground truncate">{perfil.email}</p>
                      </div>
                    </div>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-8 w-8 text-muted-foreground hover:text-red-500 opacity-0 group-hover:opacity-100 transition-opacity"
                      onClick={(e) => {
                        e.stopPropagation()
                        removeProfile(perfil.email)
                      }}
                    >
                      <X className="w-4 h-4" />
                    </Button>
                  </div>
                ))}
              </div>
            </div>
          )}

          <Card className="border-border/50 shadow-sm text-left">
            <CardHeader className="pb-3">
              <CardTitle className="text-base font-medium flex items-center gap-2">
                <User className="w-4 h-4 text-primary" />
                {isCadastro ? 'Criar uma nova conta' : savedProfiles.length > 0 ? 'Acessar com outra conta' : 'Acesse sua conta'}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleAuthSubmit} className="space-y-4">
                {isCadastro && (
                  <div className="space-y-1">
                    <label className="text-xs font-semibold text-muted-foreground">Nome</label>
                    <input
                      type="text"
                      required
                      className="w-full bg-secondary/50 border border-border rounded-md p-2 text-sm text-foreground focus:outline-none focus:border-primary"
                      value={authForm.nome}
                      onChange={e => setAuthForm({ ...authForm, nome: e.target.value })}
                    />
                  </div>
                )}
                <div className="space-y-1">
                  <label className="text-xs font-semibold text-muted-foreground">Email</label>
                  <input
                    type="email"
                    required
                    className="w-full bg-secondary/50 border border-border rounded-md p-2 text-sm text-foreground focus:outline-none focus:border-primary"
                    value={authForm.email}
                    onChange={e => setAuthForm({ ...authForm, email: e.target.value })}
                  />
                </div>
                <div className="space-y-1">
                  <label className="text-xs font-semibold text-muted-foreground">Senha</label>
                  <input
                    type="password"
                    required
                    className="w-full bg-secondary/50 border border-border rounded-md p-2 text-sm text-foreground focus:outline-none focus:border-primary"
                    value={authForm.senha}
                    onChange={e => setAuthForm({ ...authForm, senha: e.target.value })}
                  />
                </div>

                {authError && <p className="text-xs text-red-500 font-medium">{authError}</p>}

                <Button type="submit" disabled={isLoadingAuth} className="w-full gap-2" size="lg">
                  {isLoadingAuth ? (
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  ) : (
                    <>
                      <LogIn className="w-4 h-4" />
                      {isCadastro ? "Criar Conta" : "Conectar Conta"}
                    </>
                  )}
                </Button>
              </form>

              <div className="text-center mt-4">
                <button
                  type="button"
                  className="text-xs text-primary hover:underline"
                  onClick={() => {
                    setIsCadastro(!isCadastro)
                    setAuthError('')
                  }}
                >
                  {isCadastro ? "Já tem conta? Faça login" : "Não tem conta? Cadastre-se"}
                </button>
              </div>
            </CardContent>
          </Card>
          <p className="text-xs text-muted-foreground">Versão de demonstração • Dados de mercado podem ter atraso</p>
        </div>
      </div>
    )
  }

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

  if (!temInvestimentos) {
    return (
      <div className="min-h-screen bg-background flex flex-col">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 w-full flex-grow flex flex-col">
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
          
          <footer className="mt-auto pt-8 border-t border-border/50">
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

  return (
    <div className="min-h-screen bg-background flex flex-col">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 w-full flex-grow flex flex-col">
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

        {/* --- PRIMEIRA LINHA: Gráfico + Quick Actions --- */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          <div className="lg:col-span-2">
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

        {/* --- SEGUNDA LINHA: Alocação + Transações --- */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          <div className="lg:col-span-1">
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

        {/* --- TERCEIRA LINHA: Tabela de Ativos --- */}
        <div className="w-full mb-8">
          <HoldingsTable assets={(portfolio?.assets ?? []) as any} />
        </div>

        {/* --- FOOTER: Sempre no final --- */}
        <footer className="mt-auto pt-8 border-t border-border/50">
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

      {/* --- MODAIS --- */}
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
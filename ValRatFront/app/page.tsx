'use client'

import { useState } from 'react'

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

  fetchPortfolioData,

  fetchHistorico,

  fetchBenchmarks

} from '@/lib/api'

import {

  CompraModal

} from '@/components/dashboard/compra-modal'

import {

  RendimentoModal

} from '@/components/dashboard/rendimento-modal'

import {

  RetiradaModal

} from '@/components/dashboard/retirada-modal'

import {

  PatrimonioChart

} from '@/components/dashboard/patrimonio-chart'

import {

  BenchmarkCard

} from '@/components/dashboard/benchmark-card'

import {

  Card,

  CardContent,

  CardHeader,

  CardTitle

} from '@/components/ui/card'

import {

  TrendingUp,

  Wallet,

  Landmark,

  PieChart

} from 'lucide-react'


export default function DashboardPage() {

  const [openCompra, setOpenCompra] =
    useState(false)

  const [
    isRendimentoOpen,
    setIsRendimentoOpen
  ] = useState(false)

  const [
    openRetirada,
    setOpenRetirada
  ] = useState(false)

  const {

    data: portfolio,

    isLoading,

    mutate

  } = useSWR(

    'portfolio',

    fetchPortfolioData,

    {

      refreshInterval: 0,

      revalidateOnFocus: false
    }
  )

  const {

    data: historico

  } = useSWR(

    'historico',

    fetchHistorico,

    {

      refreshInterval: 0,

      revalidateOnFocus: false
    }
  )

  const {

    data: benchmarks

  } = useSWR(

    'benchmarks',

    fetchBenchmarks
  )

  const hasInvestments = (

    portfolio &&
    portfolio.assets.length > 0
  )

  return (

    <div className="
      min-h-screen
      bg-background
    ">

      <div className="
        max-w-7xl
        mx-auto
        px-4
        sm:px-6
        lg:px-8
        py-8
      ">

        <DashboardHeader
          userName="Pedro"
        />

        {/* STATS */}
        <div className="mb-8">

          <StatsGrid

            totalBalance={
              portfolio?.totalBalance ?? 0
            }

            totalInvested={
              portfolio?.totalInvested ?? 0
            }

            profitLoss={
              portfolio?.profitLoss ?? 0
            }

            percentChange={
              portfolio?.percentChange ?? 0
            }

            isLoading={isLoading}
          />

        </div>

        {!isLoading && !hasInvestments ? (

          <EmptyState

            onAddInvestment={() =>
              setOpenCompra(true)
            }
          />

        ) : (

          <>

            {/* TOP GRID */}
            <div className="
              grid
              grid-cols-1
              lg:grid-cols-3
              gap-6
              mb-8
            ">

              {/* LEFT */}
              <div className="
                lg:col-span-2
                space-y-6
              ">

                <WalletCard

                  totalBalance={
                    portfolio?.totalBalance ?? 0
                  }

                  profitLoss={
                    portfolio?.profitLoss ?? 0
                  }

                  percentChange={
                    portfolio?.percentChange ?? 0
                  }

                  historicalData={
                    portfolio?.historicalData ?? []
                  }

                  isLoading={isLoading}
                />

                <PatrimonioChart
                  historico={
                    historico ?? []
                  }
                />

              </div>

              {/* RIGHT */}
              <div className="
                lg:col-span-1
                space-y-6
              ">

                <QuickActions

                  onComprarClick={() =>
                    setOpenCompra(true)
                  }

                  onSimularRendimentoClick={() =>
                    setIsRendimentoOpen(true)
                  }

                  onVenderClick={() =>
                    setOpenRetirada(true)
                  }
                />

                {/* RESUMO */}
                <Card className="
                  border-border/50
                  shadow-sm
                ">

                  <CardHeader>

                    <CardTitle>

                      Resumo Geral

                    </CardTitle>

                  </CardHeader>

                  <CardContent>

                    <div className="
                      space-y-5
                    ">

                      <div className="
                        flex
                        items-center
                        justify-between
                      ">

                        <div className="
                          flex
                          items-center
                          gap-3
                        ">

                          <Wallet
                            className="
                              w-5
                              h-5
                              text-primary
                            "
                          />

                          <span>

                            Patrimônio

                          </span>

                        </div>

                        <span className="
                          font-semibold
                        ">

                          {new Intl.NumberFormat(
                            'pt-BR',
                            {
                              style: 'currency',
                              currency: 'BRL'
                            }
                          ).format(
                            portfolio?.totalBalance ?? 0
                          )}

                        </span>

                      </div>

                      <div className="
                        flex
                        items-center
                        justify-between
                      ">

                        <div className="
                          flex
                          items-center
                          gap-3
                        ">

                          <Landmark
                            className="
                              w-5
                              h-5
                              text-primary
                            "
                          />

                          <span>

                            Investido

                          </span>

                        </div>

                        <span className="
                          font-semibold
                        ">

                          {new Intl.NumberFormat(
                            'pt-BR',
                            {
                              style: 'currency',
                              currency: 'BRL'
                            }
                          ).format(
                            portfolio?.totalInvested ?? 0
                          )}

                        </span>

                      </div>

                      <div className="
                        flex
                        items-center
                        justify-between
                      ">

                        <div className="
                          flex
                          items-center
                          gap-3
                        ">

                          <TrendingUp
                            className="
                              w-5
                              h-5
                              text-primary
                            "
                          />

                          <span>

                            Lucro

                          </span>

                        </div>

                        <span className={`
                          font-semibold
                          ${
                            (
                              portfolio?.profitLoss ?? 0
                            ) >= 0
                              ? 'text-green-500'
                              : 'text-red-500'
                          }
                        `}>

                          {new Intl.NumberFormat(
                            'pt-BR',
                            {
                              style: 'currency',
                              currency: 'BRL'
                            }
                          ).format(
                            portfolio?.profitLoss ?? 0
                          )}

                        </span>

                      </div>

                      <div className="
                        flex
                        items-center
                        justify-between
                      ">

                        <div className="
                          flex
                          items-center
                          gap-3
                        ">

                          <PieChart
                            className="
                              w-5
                              h-5
                              text-primary
                            "
                          />

                          <span>

                            Ativos

                          </span>

                        </div>

                        <span className="
                          font-semibold
                        ">

                          {
                            portfolio?.assets
                              ?.length ?? 0
                          }

                        </span>

                      </div>

                    </div>

                  </CardContent>

                </Card>

              </div>

            </div>

            {/* SECOND GRID */}
            <div className="
              grid
              grid-cols-1
              lg:grid-cols-3
              gap-6
              mb-8
            ">

              {/* LEFT */}
              <div className="
                lg:col-span-1
                space-y-6
              ">

                <AssetAllocation

                  allocations={
                    portfolio?.allocations ?? []
                  }

                  isLoading={isLoading}
                />

                <BenchmarkCard

                  carteira={
                    benchmarks?.carteira ?? 0
                  }

                  cdi={
                    benchmarks?.cdi ?? 0
                  }

                  selic={
                    benchmarks?.selic ?? 0
                  }

                  ibov={
                    benchmarks?.ibov ?? 0
                  }
                />

              </div>

              {/* RIGHT */}
              <div className="
                lg:col-span-2
              ">

                <TransactionLedger

                  transactions={
                    portfolio?.transactions ?? []
                  }

                  isLoading={isLoading}
                />

              </div>

            </div>

            {/* HOLDINGS */}
            <div className="mb-8">

              <HoldingsTable

                assets={
                  portfolio?.assets ?? []
                }

                isLoading={isLoading}
              />

            </div>

          </>

        )}

        {/* FOOTER */}
        <footer className="
          mt-12
          pt-8
          border-t
          border-border/50
        ">

          <div className="
            flex
            flex-col
            sm:flex-row
            items-center
            justify-between
            gap-4
            text-sm
            text-muted-foreground
          ">

            <div className="
              flex
              items-center
              gap-2
            ">

              <span className="
                font-bold
                text-primary
              ">

                Val

              </span>

              <span className="
                font-bold
                text-foreground
              ">

                Rat

              </span>

              <span>

                © 2026

              </span>

            </div>

            <p className="
              text-center
              sm:text-right
            ">

              Dados de mercado podem ter atraso.
              Não é recomendação de investimento.

            </p>

          </div>

        </footer>

      </div>

      <CompraModal

        open={openCompra}

        onClose={() =>
          setOpenCompra(false)
        }

        onSuccess={() =>
          mutate()
        }
      />

      <RendimentoModal

        open={isRendimentoOpen}

        onOpenChange={
          setIsRendimentoOpen
        }
      />

      <RetiradaModal

        open={openRetirada}

        onClose={() =>
          setOpenRetirada(false)
        }

        onSuccess={() =>
          mutate()
        }

        assets={
          portfolio?.assets ?? []
        }
      />

    </div>
  )
}
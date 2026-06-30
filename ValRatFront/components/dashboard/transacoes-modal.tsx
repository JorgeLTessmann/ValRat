'use client'

import { useMemo, useState } from 'react'
import {
  ArrowUpRight,
  ArrowDownRight,
  Coins,
  Wallet,
  CircleDollarSign,
  Clock,
  ListFilter
} from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from '@/components/ui/dialog'
import type { Transaction } from '@/lib/types'
import { assetTypeLabels } from '@/lib/types'

interface TransacoesModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  transactions: Transaction[]
}

type FiltroTipo = 'all' | Transaction['type']

const filtros: { id: FiltroTipo; label: string }[] = [
  { id: 'all', label: 'Tudo' },
  { id: 'buy', label: 'Compra' },
  { id: 'sell', label: 'Venda' },
  { id: 'dividend', label: 'Dividendo' },
  { id: 'deposit', label: 'Depósito' },
  { id: 'withdraw', label: 'Resgate' },
]

const formatCurrency = (value: number) =>
  new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value)

const formatDate = (dateStr: string) => {
  const date = new Date(dateStr)
  if (Number.isNaN(date.getTime())) return dateStr
  return new Intl.DateTimeFormat('pt-BR', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }).format(date)
}

const getTransactionIcon = (type: Transaction['type']) => {
  switch (type) {
    case 'buy': return <ArrowDownRight className="h-4 w-4" />
    case 'sell': return <ArrowUpRight className="h-4 w-4" />
    case 'dividend': return <Coins className="h-4 w-4" />
    case 'deposit': return <Wallet className="h-4 w-4" />
    case 'withdraw': return <CircleDollarSign className="h-4 w-4" />
    default: return <CircleDollarSign className="h-4 w-4" />
  }
}

const getTransactionLabel = (type: Transaction['type']) => {
  const labels: Record<Transaction['type'], string> = {
    buy: 'Compra',
    sell: 'Venda',
    dividend: 'Dividendo',
    deposit: 'Depósito',
    withdraw: 'Resgate'
  }
  return labels[type] ?? 'Transação'
}

const getTransactionColor = (type: Transaction['type']) => {
  switch (type) {
    case 'buy':
    case 'deposit':
      return 'text-emerald-500 dark:text-emerald-400 bg-emerald-500/10'
    case 'sell':
    case 'withdraw':
      return 'text-rose-500 dark:text-rose-400 bg-rose-500/10'
    case 'dividend':
      return 'text-primary bg-primary/10'
    default:
      return 'text-muted-foreground bg-muted'
  }
}

const getStatusBadge = (status: Transaction['status']) => {
  switch (status) {
    case 'success':
      return (
        <Badge variant="outline" className="text-emerald-600 dark:text-emerald-400 border-emerald-500/20 bg-emerald-500/5 text-[10px] font-semibold py-0 px-2">
          Concluído
        </Badge>
      )
    case 'pending':
      return (
        <Badge variant="outline" className="text-amber-600 dark:text-amber-400 border-amber-500/20 bg-amber-500/5 text-[10px] font-semibold py-0 px-2">
          Pendente
        </Badge>
      )
    case 'failed':
      return (
        <Badge variant="outline" className="text-rose-600 dark:text-rose-400 border-rose-500/20 bg-rose-500/5 text-[10px] font-semibold py-0 px-2">
          Falhou
        </Badge>
      )
  }
}

export function TransacoesModal({ open, onOpenChange, transactions }: TransacoesModalProps) {
  const [filtroAtivo, setFiltroAtivo] = useState<FiltroTipo>('all')

  const transacoesOrdenadas = useMemo(() => {
    return [...transactions].sort(
      (a, b) => new Date(b.date).getTime() - new Date(a.date).getTime()
    )
  }, [transactions])

  const transacoesFiltradas = useMemo(() => {
    if (filtroAtivo === 'all') return transacoesOrdenadas
    return transacoesOrdenadas.filter((t) => t.type === filtroAtivo)
  }, [transacoesOrdenadas, filtroAtivo])

  const contagemPorTipo = useMemo(() => {
    const contagem: Record<string, number> = { all: transacoesOrdenadas.length }
    for (const t of transacoesOrdenadas) {
      contagem[t.type] = (contagem[t.type] ?? 0) + 1
    }
    return contagem
  }, [transacoesOrdenadas])

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-xl border-border/60 bg-card p-6 overflow-hidden before:absolute before:inset-x-0 before:top-0 before:h-[2px] before:bg-gradient-to-r before:from-transparent before:via-primary/40 before:to-transparent">
        <DialogHeader className="space-y-1">
          <DialogTitle className="flex items-center gap-2 text-foreground font-bold tracking-tight pr-6">
            <ListFilter className="h-4 w-4 text-primary" />
            Todas as Transações
          </DialogTitle>
          <DialogDescription className="text-xs text-muted-foreground">
            Histórico completo de movimentações da sua carteira.
          </DialogDescription>
        </DialogHeader>

        {/* Filtros por tipo */}
        <div className="flex flex-wrap gap-1.5">
          {filtros.map((filtro) => {
            const quantidade = contagemPorTipo[filtro.id] ?? 0
            const ativo = filtroAtivo === filtro.id
            return (
              <button
                key={filtro.id}
                onClick={() => setFiltroAtivo(filtro.id)}
                className={cn(
                  'rounded-full px-3 py-1.5 text-xs font-semibold transition-all border',
                  ativo
                    ? 'bg-primary text-primary-foreground border-primary shadow-sm'
                    : 'bg-secondary/40 text-muted-foreground border-border/60 hover:bg-secondary hover:text-foreground'
                )}
              >
                {filtro.label}
                <span className={cn('ml-1.5 opacity-70', ativo ? 'text-primary-foreground' : 'text-muted-foreground')}>
                  {quantidade}
                </span>
              </button>
            )
          })}
        </div>

        {/* Lista de transações */}
        <div className="mt-1 max-h-[420px] space-y-2 overflow-y-auto pr-1">
          {transacoesFiltradas.length === 0 && (
            <div className="rounded-lg border border-border/40 bg-secondary/30 px-3 py-6 text-center text-xs text-muted-foreground">
              Nenhuma transação encontrada para esse filtro.
            </div>
          )}

          {transacoesFiltradas.map((transaction) => {
            const isNegativeAmount = transaction.type === 'sell' || transaction.type === 'withdraw'

            return (
              <div
                key={transaction.id}
                className="flex items-center justify-between p-3 rounded-xl border border-border/40 bg-muted/30 hover:bg-muted/60 transition-all duration-200"
              >
                <div className="flex items-center gap-3 min-w-0">
                  <div className={cn(
                    'w-10 h-10 rounded-full flex items-center justify-center shrink-0',
                    getTransactionColor(transaction.type)
                  )}>
                    {getTransactionIcon(transaction.type)}
                  </div>

                  <div className="min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="text-sm font-semibold tracking-tight text-foreground">
                        {getTransactionLabel(transaction.type)}
                      </span>
                      {transaction.ticker && (
                        <Badge variant="secondary" className="text-[11px] font-mono font-bold bg-muted text-muted-foreground border border-border/40 rounded-md py-0 px-1.5 shadow-none">
                          {transaction.ticker}
                        </Badge>
                      )}
                    </div>

                    <div className="flex items-center gap-1.5 text-xs text-muted-foreground mt-0.5 truncate">
                      <Clock className="h-3 w-3 shrink-0" />
                      <span className="font-mono font-medium">{formatDate(transaction.date)}</span>
                      {transaction.assetType && (
                        <>
                          <span className="text-muted-foreground/40">•</span>
                          <span className="truncate">{assetTypeLabels[transaction.assetType]}</span>
                        </>
                      )}
                    </div>
                  </div>
                </div>

                <div className="text-right pl-3 shrink-0">
                  <div className={cn(
                    'text-sm font-bold font-mono tracking-tight',
                    isNegativeAmount
                      ? 'text-rose-600 dark:text-rose-400'
                      : 'text-emerald-600 dark:text-emerald-400'
                  )}>
                    {isNegativeAmount ? '-' : '+'}
                    {formatCurrency(transaction.amount).replace('R$', '').trim()}
                    <span className="text-xs font-medium ml-0.5 text-muted-foreground">BRL</span>
                  </div>
                  <div className="mt-1 flex justify-end">
                    {getStatusBadge(transaction.status)}
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      </DialogContent>
    </Dialog>
  )
}
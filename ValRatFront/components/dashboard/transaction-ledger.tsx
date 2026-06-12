'use client'

import { 
  ArrowUpRight, 
  ArrowDownRight, 
  Coins, 
  Wallet,
  CircleDollarSign,
  Clock
} from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { cn } from '@/lib/utils'
import type { Transaction } from '@/lib/types'
import { assetTypeLabels } from '@/lib/types'

interface TransactionLedgerProps {
  transactions: Transaction[]
  isLoading?: boolean
}

export function TransactionLedger({ transactions, isLoading }: TransactionLedgerProps) {
  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value)
  }

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr)
    return new Intl.DateTimeFormat('pt-BR', {
      day: '2-digit',
      month: 'short',
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
    const labels = {
      buy: 'Compra',
      sell: 'Venda',
      dividend: 'Dividendo',
      deposit: 'Depósito',
      withdraw: 'Resgate'
    }
    return labels[type]
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

  if (isLoading) {
    return (
      <Card className="border-border/60 shadow-sm">
        <CardHeader className="pb-3">
          <Skeleton className="h-5 w-48" />
        </CardHeader>
        <CardContent className="space-y-2.5">
          {[1, 2, 3].map((i) => (
            <div key={i} className="flex items-center justify-between p-3 border border-border/40 rounded-xl">
              <div className="flex items-center gap-3">
                <Skeleton className="h-10 w-10 rounded-full" />
                <div className="space-y-1.5">
                  <Skeleton className="h-4 w-24" />
                  <Skeleton className="h-3 w-36" />
                </div>
              </div>
              <Skeleton className="h-4 w-16" />
            </div>
          ))}
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="border-border/60 shadow-sm bg-card">
      <CardHeader className="pb-3">
        <CardTitle className="text-xs font-bold text-muted-foreground uppercase tracking-wider">
          Histórico de Transações
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-2.5">
        {transactions.slice(0, 6).map((transaction) => {
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
                    {/* Texto com fonte normal do sistema */}
                    <span className="text-sm font-semibold tracking-tight text-foreground">
                      {getTransactionLabel(transaction.type)}
                    </span>
                    {transaction.ticker && (
                      <Badge variant="secondary" className="text-[11px] font-mono font-bold bg-muted text-muted-foreground border border-border/40 rounded-md py-0 px-1.5 shadow-none">
                        {transaction.ticker}
                      </Badge>
                    )}
                  </div>
                  
                  {/* Data em fonte mono para manter o alinhamento das horas */}
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
                {/* Dinheiro estritamente em fonte quadrada (mono) */}
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
                <div className="mt-1">
                  {getStatusBadge(transaction.status)}
                </div>
              </div>
            </div>
          )
        })}

        {transactions.length > 6 && (
          <button className="w-full mt-2 py-2.5 text-xs font-bold uppercase tracking-wider text-muted-foreground hover:text-[#D4AF37] hover:border-amber-500/30 hover:bg-amber-500/[0.02] border border-dashed border-border rounded-xl transition-all duration-150">
            Ver todas as transações
          </button>
        )}
      </CardContent>
    </Card>
  )
}
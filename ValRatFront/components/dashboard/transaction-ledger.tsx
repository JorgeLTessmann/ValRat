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
      case 'buy':
        return <ArrowDownRight className="h-4 w-4" />
      case 'sell':
        return <ArrowUpRight className="h-4 w-4" />
      case 'dividend':
        return <Coins className="h-4 w-4" />
      case 'deposit':
        return <Wallet className="h-4 w-4" />
      case 'withdraw':
        return <CircleDollarSign className="h-4 w-4" />
      default:
        return <CircleDollarSign className="h-4 w-4" />
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
        return 'text-emerald-600 bg-emerald-50'
      case 'sell':
      case 'withdraw':
        return 'text-red-600 bg-red-50'
      case 'dividend':
        return 'text-primary bg-accent'
      default:
        return 'text-muted-foreground bg-muted'
    }
  }

  const getStatusBadge = (status: Transaction['status']) => {
    switch (status) {
      case 'success':
        return <Badge variant="outline" className="text-emerald-600 border-emerald-200 bg-emerald-50/50 text-xs">Concluído</Badge>
      case 'pending':
        return <Badge variant="outline" className="text-amber-600 border-amber-200 bg-amber-50/50 text-xs">Pendente</Badge>
      case 'failed':
        return <Badge variant="outline" className="text-red-600 border-red-200 bg-red-50/50 text-xs">Falhou</Badge>
    }
  }

  if (isLoading) {
    return (
      <Card className="border-border/50 shadow-sm">
        <CardHeader className="pb-4">
          <Skeleton className="h-6 w-40" />
        </CardHeader>
        <CardContent className="space-y-3">
          {[1, 2, 3, 4, 5].map((i) => (
            <Skeleton key={i} className="h-16 w-full" />
          ))}
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="border-border/50 shadow-sm hover:shadow-md transition-shadow duration-300">
      <CardHeader className="pb-4">
        <CardTitle className="text-lg font-semibold text-accent-foreground">
          Histórico de Transações
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-2">
        {transactions.slice(0, 6).map((transaction) => (
          <div
            key={transaction.id}
            className="flex items-center justify-between p-3 rounded-xl bg-secondary/30 hover:bg-secondary/50 transition-colors duration-200"
          >
            <div className="flex items-center gap-3">
              <div className={cn(
                'w-10 h-10 rounded-full flex items-center justify-center',
                getTransactionColor(transaction.type)
              )}>
                {getTransactionIcon(transaction.type)}
              </div>
              
              <div>
                <div className="flex items-center gap-2">
                  <span className="font-medium text-foreground">
                    {getTransactionLabel(transaction.type)}
                  </span>
                  {transaction.ticker && (
                    <Badge variant="secondary" className="text-xs font-mono bg-secondary text-secondary-foreground">
                      {transaction.ticker}
                    </Badge>
                  )}
                </div>
                <div className="flex items-center gap-1.5 text-xs text-muted-foreground mt-0.5">
                  <Clock className="h-3 w-3" />
                  <span>{formatDate(transaction.date)}</span>
                  {transaction.assetType && (
                    <>
                      <span>•</span>
                      <span>{assetTypeLabels[transaction.assetType]}</span>
                    </>
                  )}
                </div>
              </div>
            </div>

            <div className="text-right">
              <div className={cn(
                'font-semibold',
                transaction.type === 'sell' || transaction.type === 'withdraw'
                  ? 'text-red-600'
                  : 'text-emerald-600'
              )}>
                {transaction.type === 'sell' || transaction.type === 'withdraw' ? '-' : '+'}
                {formatCurrency(transaction.amount)}
              </div>
              <div className="mt-1">
                {getStatusBadge(transaction.status)}
              </div>
            </div>
          </div>
        ))}

        {transactions.length > 6 && (
          <button className="w-full py-3 text-sm font-medium text-primary hover:text-primary/80 transition-colors">
            Ver todas as transações
          </button>
        )}
      </CardContent>
    </Card>
  )
}

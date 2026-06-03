'use client'

import { useState, useMemo } from 'react'
import {
  ArrowUpDown,
  Search,
  TrendingUp,
  TrendingDown,
  ChevronDown,
  ChevronUp
} from 'lucide-react'
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle
} from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow
} from '@/components/ui/table'
import { cn } from '@/lib/utils'
import type { Asset } from '@/lib/types'
import { assetTypeLabels } from '@/lib/types'

interface HoldingsTableProps {
  assets: Asset[]
  isLoading?: boolean
}

type SortField = 'ticker' | 'currentValue' | 'profitLoss' | 'percentChange' | 'data_compra'
type SortDirection = 'asc' | 'desc'

export function HoldingsTable({ assets, isLoading }: HoldingsTableProps) {
  const [searchQuery, setSearchQuery] = useState('')
  const [sortField, setSortField] = useState<SortField>('currentValue')
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc')

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value)
  }

  const formatPercent = (value: number) => {
    return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`
  }

  const formatDate = (dateStr: string) => {
    if (!dateStr) return '-'
    const parts = dateStr.split('-')
    if (parts.length === 3) {
      return `${parts[2]}/${parts[1]}/${parts[0]}`
    }
    return dateStr
  }

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc')
    } else {
      setSortField(field)
      setSortDirection('desc')
    }
  }

  const filteredAndSortedAssets = useMemo(() => {
    let filtered = assets.filter(
      asset =>
        asset.ticker.toLowerCase().includes(searchQuery.toLowerCase()) ||
        asset.name.toLowerCase().includes(searchQuery.toLowerCase())
    )

    filtered.sort((a, b) => {
      let aValue: any = a[sortField as keyof Asset]
      let bValue: any = b[sortField as keyof Asset]
      
      if (sortField === 'data_compra') {
        aValue = a.data_compra || ''
        bValue = b.data_compra || ''
      }
      
      if (typeof aValue === 'string' && typeof bValue === 'string') {
        return sortDirection === 'asc'
          ? aValue.localeCompare(bValue)
          : bValue.localeCompare(aValue)
      }
      return sortDirection === 'asc'
        ? (aValue as number) - (bValue as number)
        : (bValue as number) - (aValue as number)
    })

    return filtered
  }, [assets, searchQuery, sortField, sortDirection])

  const getTypeBadgeColor = (type: Asset['type']) => {
    const colors: Record<Asset['type'], string> = {
      acao: 'bg-primary/10 text-primary border-primary/20',
      etf: 'bg-accent text-accent-foreground border-accent-foreground/20',
      fii: 'bg-amber-50 text-amber-700 border-amber-200',
      fundo: 'bg-blue-50 text-blue-700 border-blue-200',
      cdb: 'bg-emerald-50 text-emerald-700 border-emerald-200',
      lci: 'bg-violet-50 text-violet-700 border-violet-200',
      lca: 'bg-pink-50 text-pink-700 border-pink-200',
      tesouro: 'bg-green-50 text-green-700 border-green-200'
    }
    return colors[type] || 'bg-secondary/50 text-secondary-foreground'
  }

  const SortIcon = ({ field }: { field: SortField }) => {
    if (sortField !== field) {
      return <ArrowUpDown className="h-3.5 w-3.5 text-muted-foreground/50" />
    }
    return sortDirection === 'asc'
      ? <ChevronUp className="h-3.5 w-3.5 text-primary" />
      : <ChevronDown className="h-3.5 w-3.5 text-primary" />
  }

  if (isLoading) {
    return (
      <Card className="border-border/50 shadow-sm">
        <CardHeader className="pb-4">
          <Skeleton className="h-6 w-40" />
          <Skeleton className="h-10 w-full mt-4" />
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {[1, 2, 3, 4, 5].map((i) => (
              <Skeleton key={i} className="h-14 w-full" />
            ))}
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="border-border/50 shadow-sm hover:shadow-md transition-shadow duration-300">
      <CardHeader className="pb-4">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <CardTitle className="text-lg font-semibold text-accent-foreground">
            Meus Ativos
          </CardTitle>
          <div className="relative w-full sm:w-64">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Buscar ativo..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-9 bg-secondary/30 border-border/50 focus:border-primary/50"
            />
          </div>
        </div>
      </CardHeader>

      <CardContent>
        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow className="border-border/50 hover:bg-transparent">
                <TableHead className="w-[180px]">
                  <Button variant="ghost" size="sm" className="h-auto p-0 font-semibold text-muted-foreground hover:text-foreground" onClick={() => handleSort('ticker')}>
                    Ativo <SortIcon field="ticker" />
                  </Button>
                </TableHead>
                <TableHead className="text-center">Tipo</TableHead>
                <TableHead className="text-right">Qtd</TableHead>
                <TableHead className="text-right">PM</TableHead>
                <TableHead className="text-right">Atual</TableHead>
                <TableHead className="text-right">
                  <Button variant="ghost" size="sm" className="h-auto p-0 font-semibold text-muted-foreground hover:text-foreground ml-auto" onClick={() => handleSort('currentValue')}>
                    Valor <SortIcon field="currentValue" />
                  </Button>
                </TableHead>
                <TableHead className="text-right">
                  <Button variant="ghost" size="sm" className="h-auto p-0 font-semibold text-muted-foreground hover:text-foreground ml-auto" onClick={() => handleSort('profitLoss')}>
                    Lucro/Prejuízo <SortIcon field="profitLoss" />
                  </Button>
                </TableHead>
                <TableHead className="text-right">
                  <Button variant="ghost" size="sm" className="h-auto p-0 font-semibold text-muted-foreground hover:text-foreground ml-auto" onClick={() => handleSort('percentChange')}>
                    Variação <SortIcon field="percentChange" />
                  </Button>
                </TableHead>
                <TableHead className="text-right">
                  <Button variant="ghost" size="sm" className="h-auto p-0 font-semibold text-muted-foreground hover:text-foreground ml-auto" onClick={() => handleSort('data_compra')}>
                    Data Compra <SortIcon field="data_compra" />
                  </Button>
                </TableHead>
              </TableRow>
            </TableHeader>

            <TableBody>
              {filteredAndSortedAssets.map((asset) => (
                <TableRow key={asset.id} className="border-border/30 hover:bg-secondary/30 transition-colors">
                  <TableCell>
                    <div className="flex flex-col">
                      <span className="font-semibold text-foreground font-mono">{asset.ticker}</span>
                      <span className="text-xs text-muted-foreground truncate max-w-[150px]">{asset.name}</span>
                      <span className="text-[11px] text-primary font-medium">{asset.plataforma}</span>
                    </div>
                  </TableCell>

                  <TableCell className="text-center">
                    <Badge className={cn("border", getTypeBadgeColor(asset.type))}>
                      {assetTypeLabels[asset.type] || asset.type}
                    </Badge>
                  </TableCell>

                  <TableCell className="text-right font-mono">
                    {asset.quantity}
                  </TableCell>

                  <TableCell className="text-right font-mono">
                    {formatCurrency(asset.averagePrice)}
                  </TableCell>

                  <TableCell className="text-right font-mono">
                    {formatCurrency(asset.currentPrice)}
                  </TableCell>

                  <TableCell className="text-right font-semibold">
                    {formatCurrency(asset.currentValue)}
                  </TableCell>

                  <TableCell className={cn(
                    "text-right font-semibold",
                    asset.profitLoss >= 0 ? "text-emerald-600" : "text-red-600"
                  )}>
                    {formatCurrency(asset.profitLoss)}
                  </TableCell>

                  <TableCell className={cn(
                    "text-right font-semibold",
                    asset.percentChange >= 0 ? "text-emerald-600" : "text-red-600"
                  )}>
                    {formatPercent(asset.percentChange)}
                  </TableCell>

                  <TableCell className="text-right font-mono text-sm">
                    {formatDate(asset.data_compra || '')}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  )
}
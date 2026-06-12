'use client'

import { useState } from 'react'
import { Search, TrendingUp, TrendingDown, Eye, MoreHorizontal, ArrowUpDown } from 'lucide-react'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { cn } from '@/lib/utils'

interface Asset {
  id: string
  ticker: string | null
  name: string | null
  type: string
  type_label: string
  quantity: number | null
  averagePrice: number
  currentPrice: number
  totalInvested: number
  currentValue: number
  profitLoss: number
  percentChange: number
  plataforma?: string
  data_compra?: string
}

interface HoldingsTableProps {
  assets: Asset[]
  onViewDetails?: (asset: Asset) => void
}

export function HoldingsTable({ assets, onViewDetails }: HoldingsTableProps) {
  const [searchTerm, setSearchTerm] = useState('')
  const [sortField, setSortField] = useState<keyof Asset>('currentValue')
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('desc')

  const handleSort = (field: keyof Asset) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc')
    } else {
      setSortField(field)
      setSortDirection('desc')
    }
  }

  const formatCurrency = (value: number) => {
    return value.toLocaleString('pt-BR', {
      style: 'currency',
      currency: 'BRL',
    })
  }

  const formatPercent = (value: number) => {
    return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`
  }

  const filteredAndSortedAssets = [...assets]
    .filter(asset => {
      const ticker = (asset.ticker || '').toLowerCase()
      const name = (asset.name || '').toLowerCase()
      const search = searchTerm.toLowerCase()
      return ticker.includes(search) || name.includes(search)
    })
    .sort((a, b) => {
      const aValue = a[sortField] ?? 0
      const bValue = b[sortField] ?? 0
      if (sortDirection === 'asc') {
        return aValue > bValue ? 1 : -1
      } else {
        return aValue < bValue ? 1 : -1
      }
    })

  const getProfitLossColor = (value: number) => {
    if (value > 0) return 'text-emerald-500'
    if (value < 0) return 'text-rose-500'
    return 'text-muted-foreground'
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-4">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Buscar ativo..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-8"
          />
        </div>
      </div>

      <div className="rounded-lg border border-border">
        <Table>
          <TableHeader>
            <TableRow className="hover:bg-transparent">
              <TableHead className="w-[100px]">
                <Button
                  variant="ghost"
                  size="sm"
                  className="h-8 px-2 font-medium -ml-2"
                  onClick={() => handleSort('ticker')}
                >
                  Código
                  <ArrowUpDown className="ml-1 h-3 w-3" />
                </Button>
              </TableHead>
              <TableHead>Ativo</TableHead>
              <TableHead>Tipo</TableHead>
              <TableHead className="text-right">
                <Button
                  variant="ghost"
                  size="sm"
                  className="h-8 px-2 font-medium -ml-2 ml-auto"
                  onClick={() => handleSort('totalInvested')}
                >
                  Investido
                  <ArrowUpDown className="ml-1 h-3 w-3" />
                </Button>
              </TableHead>
              <TableHead className="text-right">
                <Button
                  variant="ghost"
                  size="sm"
                  className="h-8 px-2 font-medium -ml-2 ml-auto"
                  onClick={() => handleSort('currentValue')}
                >
                  Valor Atual
                  <ArrowUpDown className="ml-1 h-3 w-3" />
                </Button>
              </TableHead>
              <TableHead className="text-right">
                <Button
                  variant="ghost"
                  size="sm"
                  className="h-8 px-2 font-medium -ml-2 ml-auto"
                  onClick={() => handleSort('profitLoss')}
                >
                  Resultado
                  <ArrowUpDown className="ml-1 h-3 w-3" />
                </Button>
              </TableHead>
              <TableHead className="text-right">%</TableHead>
              <TableHead className="w-[50px]"></TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filteredAndSortedAssets.length === 0 ? (
              <TableRow>
                <TableCell colSpan={8} className="text-center py-8 text-muted-foreground">
                  Nenhum ativo encontrado
                </TableCell>
              </TableRow>
            ) : (
              filteredAndSortedAssets.map((asset) => (
                <TableRow key={asset.id} className="group">
                  <TableCell className="font-mono font-medium">
                    {asset.ticker || '-'}
                  </TableCell>
                  <TableCell>
                    <div>
                      <div className="font-medium">{asset.name || asset.ticker || 'Sem nome'}</div>
                      {asset.plataforma && (
                        <div className="text-xs text-muted-foreground">{asset.plataforma}</div>
                      )}
                    </div>
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline" className="font-normal">
                      {asset.type_label || asset.type || 'Renda Fixa'}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-right font-mono">
                    {formatCurrency(asset.totalInvested)}
                  </TableCell>
                  <TableCell className="text-right font-mono">
                    {formatCurrency(asset.currentValue)}
                  </TableCell>
                  <TableCell className={cn("text-right font-mono font-medium", getProfitLossColor(asset.profitLoss))}>
                    {asset.profitLoss >= 0 ? '+' : ''}{formatCurrency(asset.profitLoss)}
                    {asset.profitLoss !== 0 && (
                      <span className="ml-1 text-xs">
                        {asset.profitLoss > 0 ? <TrendingUp className="inline h-3 w-3" /> : <TrendingDown className="inline h-3 w-3" />}
                      </span>
                    )}
                  </TableCell>
                  <TableCell className={cn("text-right font-mono", getProfitLossColor(asset.percentChange))}>
                    {formatPercent(asset.percentChange)}
                  </TableCell>
                  <TableCell>
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button variant="ghost" size="icon" className="h-8 w-8">
                          <MoreHorizontal className="h-4 w-4" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuItem onClick={() => onViewDetails?.(asset)}>
                          <Eye className="mr-2 h-4 w-4" />
                          Ver detalhes
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>
    </div>
  )
}
'use client'

import { useState } from 'react'
import { Search, TrendingUp, TrendingDown, Eye, MoreHorizontal, ArrowUpDown, Calendar } from 'lucide-react'
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
    return value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
  }

  // Formata YYYY-MM-DD para DD/MM/AAAA
  const formatDate = (dateString: string) => {
    if (!dateString) return '-'
    const [year, month, day] = dateString.split('-')
    return `${day}/${month}/${year}`
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
      return sortDirection === 'asc' ? (aValue > bValue ? 1 : -1) : (aValue < bValue ? 1 : -1)
    })

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

      <div className="rounded-lg border border-border overflow-hidden">
        <Table>
          <TableHeader>
            <TableRow className="hover:bg-transparent">
              <TableHead className="w-[100px]">
                <Button variant="ghost" size="sm" className="h-8 px-2 font-medium -ml-2" onClick={() => handleSort('ticker')}>
                  Código <ArrowUpDown className="ml-1 h-3 w-3" />
                </Button>
              </TableHead>
              <TableHead>Ativo</TableHead>
              <TableHead>
                <Button variant="ghost" size="sm" className="h-8 px-2 font-medium -ml-2" onClick={() => handleSort('data_compra')}>
                  Data <ArrowUpDown className="ml-1 h-3 w-3" />
                </Button>
              </TableHead>
              <TableHead>Tipo</TableHead>
              <TableHead className="text-right">
                <Button variant="ghost" size="sm" className="h-8 px-2 font-medium ml-auto" onClick={() => handleSort('totalInvested')}>
                  Investido <ArrowUpDown className="ml-1 h-3 w-3" />
                </Button>
              </TableHead>
              <TableHead className="text-right">
                <Button variant="ghost" size="sm" className="h-8 px-2 font-medium ml-auto" onClick={() => handleSort('currentValue')}>
                  Valor Atual <ArrowUpDown className="ml-1 h-3 w-3" />
                </Button>
              </TableHead>
              <TableHead className="text-right">Resultado</TableHead>
              <TableHead className="text-right">%</TableHead>
              <TableHead className="w-[50px]"></TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filteredAndSortedAssets.map((asset) => (
              <TableRow key={asset.id} className="group">
                <TableCell className="font-mono font-medium">{asset.ticker || '-'}</TableCell>
                <TableCell>
                  <div className="font-medium text-xs sm:text-sm">{asset.name || asset.ticker || 'Sem nome'}</div>
                  {asset.plataforma && <div className="text-[10px] text-muted-foreground uppercase">{asset.plataforma}</div>}
                </TableCell>
                <TableCell className="text-muted-foreground text-xs whitespace-nowrap">
                  {formatDate(asset.data_compra || '')}
                </TableCell>
                <TableCell>
                  <Badge variant="outline" className="font-normal text-[10px] uppercase">
                    {asset.type_label || asset.type}
                  </Badge>
                </TableCell>
                <TableCell className="text-right font-mono text-xs">{formatCurrency(asset.totalInvested)}</TableCell>
                <TableCell className="text-right font-mono text-xs">{formatCurrency(asset.currentValue)}</TableCell>
                <TableCell className={cn("text-right font-mono font-medium text-xs", asset.profitLoss > 0 ? 'text-emerald-500' : 'text-rose-500')}>
                  {asset.profitLoss >= 0 ? '+' : ''}{formatCurrency(asset.profitLoss)}
                </TableCell>
                <TableCell className={cn("text-right font-mono text-xs", asset.percentChange > 0 ? 'text-emerald-500' : 'text-rose-500')}>
                  {asset.percentChange >= 0 ? '+' : ''}{asset.percentChange.toFixed(2)}%
                </TableCell>
                <TableCell>
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button variant="ghost" size="icon" className="h-8 w-8"><MoreHorizontal className="h-4 w-4" /></Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                      <DropdownMenuItem onClick={() => onViewDetails?.(asset)}>
                        <Eye className="mr-2 h-4 w-4" /> Ver detalhes
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  )
}
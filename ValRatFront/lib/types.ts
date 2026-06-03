// lib/types.ts

export type AssetType =
  | 'acao'
  | 'etf'
  | 'fii'
  | 'cdb'
  | 'lci'
  | 'lca'
  | 'fundo'
  | 'tesouro'

export type AssetCategory = 'variavel' | 'fixa' | 'cripto'


export interface Asset {
  id: string
  ticker: string
  name: string
  type: AssetType
  quantity: number
  averagePrice: number
  currentPrice: number
  totalInvested: number
  currentValue: number
  profitLoss: number
  percentChange: number
  plataforma: string
  data_compra?: string
}

export interface Transaction {
  id: string
  type: 'buy' | 'sell' | 'dividend' | 'deposit' | 'withdraw'
  ticker?: string
  assetType?: AssetType
  category?: AssetCategory
  amount: number
  quantity?: number
  price?: number
  date: string
  status: 'success' | 'pending' | 'failed'
}

export interface PortfolioAllocation {
  type: AssetType
  category?: AssetCategory
  label: string
  totalInvested: number
  currentValue: number
  percentage: number
}

export interface PortfolioData {
  totalBalance: number
  totalInvested: number
  profitLoss: number
  percentChange: number
  assets: Asset[]
  transactions: Transaction[]
  allocations: PortfolioAllocation[]
  historicalData: { date: string; value: number }[]
  comparisonData: { date: string; carteira: number; cdi: number; ibov: number }[]
}

// Labels para tipos de ativo (usado nos componentes)
export const assetTypeLabels: Record<AssetType, string> = {
  acao: 'Ação',
  etf: 'ETF',
  fii: 'FII',
  cdb: 'CDB',
  lci: 'LCI',
  lca: 'LCA',
  fundo: 'Fundo',
  tesouro: 'Tesouro'
}

// Cores para tipos de ativo
export const assetTypeColors: Record<AssetType, string> = {
  acao: 'bg-primary/10 text-primary border-primary/20',
  etf: 'bg-accent text-accent-foreground border-accent-foreground/20',
  fii: 'bg-amber-50 text-amber-700 border-amber-200',
  cdb: 'bg-emerald-50 text-emerald-700 border-emerald-200',
  lci: 'bg-violet-50 text-violet-700 border-violet-200',
  lca: 'bg-pink-50 text-pink-700 border-pink-200',
  fundo: 'bg-blue-50 text-blue-700 border-blue-200',
  tesouro: 'bg-green-50 text-green-700 border-green-200'
}

// Labels para categorias
export const categoryLabels: Record<AssetCategory, string> = {
  variavel: 'Renda Variável',
  fixa: 'Renda Fixa',
  cripto: 'Criptomoedas'
}

// Cores para categorias
export const categoryColors: Record<AssetCategory, string> = {
  variavel: 'bg-blue-50 text-blue-700 border-blue-200',
  fixa: 'bg-emerald-50 text-emerald-700 border-emerald-200',
  cripto: 'bg-purple-50 text-purple-700 border-purple-200'
}

// Interface para histórico de ativo
export interface HistoricoItem {
  id: number
  data: string
  patrimonio: number
  investido: number
  lucro: number
}

export type AssetType =
  | 'acao'
  | 'etf'
  | 'fii'
  | 'cdb'
  | 'lci'
  | 'lca'
  | 'fundo'

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
}

export interface Transaction {

  id: string

  type:
    | 'buy'
    | 'sell'
    | 'dividend'
    | 'deposit'
    | 'withdraw'

  ticker?: string

  assetType?: AssetType

  amount: number

  quantity?: number

  price?: number

  date: string

  status:
    | 'success'
    | 'pending'
    | 'failed'
}

export interface PortfolioAllocation {

  type: AssetType

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

  historicalData: {

    date: string

    value: number

  }[]

  comparisonData: {

    date: string

    carteira: number

    cdi: number

    ibov: number

  }[]
}

export const assetTypeLabels: Record<AssetType, string> = {

  acao: 'Ações',

  etf: 'ETFs',

  fii: 'FIIs',

  cdb: 'CDB',

  lci: 'LCI',

  lca: 'LCA',

  fundo: 'Fundos'
}

export const assetTypeColors:
Record<AssetType, string> = {

  acao: 'bg-chart-1',

  etf: 'bg-chart-2',

  fii: 'bg-chart-3',

  fundo: 'bg-chart-4',

  cdb: 'bg-chart-5',

  lci: 'bg-chart-1',

  lca: 'bg-chart-2'
}

export interface HistoricoItem {

  id: number

  data: string

  patrimonio: number

  investido: number

  lucro: number
}
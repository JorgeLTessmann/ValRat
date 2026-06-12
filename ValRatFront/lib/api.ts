// lib/api.ts
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
import type { PortfolioData, AssetCategory } from './types'

// Busca dados completos da carteira (com cache no back)
export const fetchPortfolioData = async (): Promise<PortfolioData> => {
  const response = await fetch(`${API_URL}/carteira/completa`)
  if (!response.ok) {
    throw new Error("Erro ao buscar carteira")
  }
  return response.json()
}

// Busca dados rápidos da carteira (apenas totais)
export const fetchPortfolioResumo = async () => {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 10000); // 10s

  try {
    const response = await fetch(`${API_URL}/carteira/rapida`, {
      signal: controller.signal,
    });
    clearTimeout(timeoutId);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return await response.json();
  } catch (error) {
    console.warn("Snapshot ainda não disponível, aguardando...");
    // Retorna valores padrão sem lançar erro (para não quebrar a UI)
    return { totalBalance: 0, totalInvested: 0, profitLoss: 0, percentChange: 0 };
  }
};


export const cadastrarCompra = async (compra: {
  categoria: string
  ticker: string
  data_compra: string
  quantidade: number
  plataforma: string
  valor_investido?: number
  taxa?: number
  indexador?: string
  data_vencimento?: string
}) => {
  const response = await fetch(`${API_URL}/compras`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(compra)
  })
  if (!response.ok) {
    throw new Error("Erro ao cadastrar compra")
  }
  return response.json()
}

export async function fetchHistorico() {
  const response = await fetch(`${API_URL}/historico`)
  if (!response.ok) {
    throw new Error('Erro ao buscar histórico')
  }
  return response.json()
}

export async function fetchBenchmarks() {
  const response = await fetch(`${API_URL}/benchmark`)
  if (!response.ok) {
    throw new Error('Erro ao buscar benchmarks')
  }
  return response.json()
}

export async function fetchHistoricoAtivo(ticker: string) {
  const response = await fetch(`${API_URL}/ativos/${ticker}/historico`)
  if (!response.ok) {
    throw new Error('Erro ao buscar histórico')
  }
  return response.json()
}

// Adicione esta função no arquivo lib/api.ts (depois de cadastrarCompra)

export const cadastrarRendaFixa = async (rendaFixa: {
  categoria: string
  data_compra: string
  plataforma: string
  nome_aplicacao: string
  valor_investido: number
  data_vencimento: string
  tipo_renda_fixa: string
  indexador: string
  taxa_contratada: number
  tem_carencia?: boolean
  data_carencia?: string
}) => {
  const response = await fetch(`${API_URL}/renda-fixa`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(rendaFixa)
  })
  if (!response.ok) {
    const error = await response.text()
    throw new Error(`Erro ao cadastrar renda fixa: ${error}`)
  }
  return response.json()
}
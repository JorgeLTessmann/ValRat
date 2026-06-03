// lib/api.ts
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
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
  try {
    const res = await fetch(`${API_URL}/carteira/rapida`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.error("Erro ao carregar resumo:", err);
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
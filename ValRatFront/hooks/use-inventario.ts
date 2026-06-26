"use client"

import { useCallback, useEffect, useState } from "react"
import { useAuth } from "@/hooks/use-auth"

export interface AtivoInventario {
  ticker: string
  nome: string
  tipo: string
  quantidade: number
  preco: number
  valorTotal: number
  lucro: number
  variacao: number
}

interface PortfolioResponse {
  totalBalance?: number
  totalInvested?: number
  profitLoss?: number
  percentChange?: number
  assets?: Array<Record<string, unknown>>
}

interface UseInventarioResult {
  ativos: AtivoInventario[]
  totalBalance: number
  totalInvested: number
  profitLoss: number
  percentChange: number
  isLoading: boolean
  error: string | null
  refetch: () => void
}

/**
 * Normaliza um item de "assets" vindo da API.
 *
 * O backend não tem um schema fixo documentado para cada item de `assets`
 * (ele é montado por calcular_renda_variavel / calcular_renda_fixa_das_compras /
 * calcular_renda_fixa_das_aplicacoes). Os nomes de campo abaixo seguem o padrão
 * já usado em outros endpoints do mesmo backend (ex: /ativos/{ticker}/historico),
 * com fallbacks para variações comuns (camelCase vs snake_case).
 *
 * Se o shape real for diferente, esse é o único lugar que precisa mudar.
 */
function normalizarAtivo(raw: Record<string, unknown>): AtivoInventario {
  const getNum = (...keys: string[]) => {
    for (const key of keys) {
      const v = raw[key]
      if (typeof v === "number" && !Number.isNaN(v)) return v
      if (typeof v === "string" && v.trim() !== "" && !Number.isNaN(Number(v))) {
        return Number(v)
      }
    }
    return 0
  }

  const getStr = (...keys: string[]) => {
    for (const key of keys) {
      const v = raw[key]
      if (typeof v === "string" && v.trim() !== "") return v
    }
    return ""
  }

  const ticker = getStr("ticker", "codigo", "symbol") || "—"
  const nome = getStr("nome", "name", "descricao") || ticker

  return {
    ticker,
    nome,
    tipo: getStr("tipo", "categoria", "type") || "outro",
    quantidade: getNum("quantidade", "quantity", "qtd"),
    preco: getNum("preco", "preco_atual", "price", "valorAtual"),
    valorTotal: getNum("valor_total", "valorTotal", "value", "total"),
    lucro: getNum("lucro", "profit", "profitLoss", "lucro_total"),
    variacao: getNum("variacao", "variation", "percentChange", "percentual"),
  }
}

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "https://valrat.onrender.com"

export function useInventario(open: boolean): UseInventarioResult {
  const { currentUser } = useAuth()
  const [ativos, setAtivos] = useState<AtivoInventario[]>([])
  const [totalBalance, setTotalBalance] = useState(0)
  const [totalInvested, setTotalInvested] = useState(0)
  const [profitLoss, setProfitLoss] = useState(0)
  const [percentChange, setPercentChange] = useState(0)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [version, setVersion] = useState(0)

  const userEmail =
    currentUser?.email || (typeof currentUser === "string" ? currentUser : null)

  const refetch = useCallback(() => setVersion((v) => v + 1), [])

  useEffect(() => {
    if (!open) return
    if (!userEmail) {
      setError("Usuário não identificado.")
      return
    }

    let cancelado = false
    setIsLoading(true)
    setError(null)

    fetch(`${BASE_URL}/carteira/completa`, {
      method: "GET",
      headers: { "X-User-Email": userEmail },
    })
      .then(async (res) => {
        if (!res.ok) {
          throw new Error(`Erro ao buscar carteira (status ${res.status})`)
        }
        return res.json() as Promise<PortfolioResponse>
      })
      .then((data) => {
        if (cancelado) return

        const lista = Array.isArray(data.assets) ? data.assets.map(normalizarAtivo) : []
        // Ordena por valor total decrescente — maior posição primeiro
        lista.sort((a, b) => b.valorTotal - a.valorTotal)

        setAtivos(lista)
        setTotalBalance(data.totalBalance ?? 0)
        setTotalInvested(data.totalInvested ?? 0)
        setProfitLoss(data.profitLoss ?? 0)
        setPercentChange(data.percentChange ?? 0)
      })
      .catch((err: Error) => {
        if (!cancelado) {
          console.error("[INVENTÁRIO ERRO]", err)
          setError("Não foi possível carregar o inventário agora.")
        }
      })
      .finally(() => {
        if (!cancelado) setIsLoading(false)
      })

    return () => {
      cancelado = true
    }
  }, [open, userEmail, version])

  return {
    ativos,
    totalBalance,
    totalInvested,
    profitLoss,
    percentChange,
    isLoading,
    error,
    refetch,
  }
}
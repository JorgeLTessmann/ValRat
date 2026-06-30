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
  totalInvestido: number
  lucro: number
  variacao: number
}

interface AssetRaw {
  id?: string
  ticker?: string
  name?: string
  type?: string
  quantity?: number
  averagePrice?: number
  currentPrice?: number
  totalInvested?: number
  currentValue?: number
  grossValue?: number
  ir?: number
  profitLoss?: number
  percentChange?: number
  plataforma?: string
  data_compra?: string
  [key: string]: unknown
}

interface PortfolioResponse {
  totalBalance?: number
  totalInvested?: number
  profitLoss?: number
  percentChange?: number
  assets?: AssetRaw[]
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
 * O backend (montar_portfolio em portfolio_service.py) retorna uma linha
 * por COMPRA individual do ativo, com o shape confirmado em produção:
 *   { ticker, name, type, quantity, averagePrice, currentPrice,
 *     totalInvested, currentValue, grossValue, ir, profitLoss, percentChange }
 *
 * Os nomes são em inglês (camelCase). Mantemos fallbacks em português/snake_case
 * só por segurança, caso o backend mude no futuro, mas a prioridade é sempre
 * o shape real confirmado.
 */
function normalizarAtivo(raw: AssetRaw): AtivoInventario {
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
  const nome = getStr("name", "nome", "descricao") || ticker

  const quantidade = getNum("quantity", "quantidade", "qtd")
  // Preço de mercado atual do ativo (não o preço médio de compra)
  const preco = getNum("currentPrice", "preco_atual", "preco", "price")

  // Valor de mercado atual da posição (quantidade * preço atual)
  let valorTotal = getNum("currentValue", "valor_total", "valorTotal", "value", "total")
  if (valorTotal === 0 && quantidade > 0 && preco > 0) {
    valorTotal = quantidade * preco
  }

  // Quanto foi de fato investido nesse lote (preço de compra * quantidade)
  const totalInvestido = getNum("totalInvested", "total_investido", "valor_investido")

  const lucro = getNum("profitLoss", "lucro", "profit", "lucro_total")
  const variacao = getNum("percentChange", "variacao", "variation", "percentual")

  return {
    ticker,
    nome,
    tipo: getStr("type", "tipo", "categoria") || "outro",
    quantidade,
    preco,
    valorTotal,
    totalInvestido,
    lucro,
    variacao,
  }
}

/**
 * Agrupa múltiplas linhas do mesmo ticker (uma por compra individual,
 * como o backend retorna) em uma única linha consolidada por ativo.
 *
 * - quantidade, valorTotal, totalInvestido, lucro: soma simples
 * - preco: o preço de mercado atual é o mesmo para todos os lotes do
 *   mesmo ticker no mesmo instante, então usamos o preço de qualquer lote
 *   processado (não precisa de média ponderada aqui)
 * - variacao: recalculada a partir do lucro agregado sobre o total
 *   investido agregado, já que a variação% de um lote isolado não
 *   representa a posição consolidada no ativo
 */
function agruparPorTicker(ativos: AtivoInventario[]): AtivoInventario[] {
  const grupos = new Map<string, AtivoInventario>()

  for (const ativo of ativos) {
    const chave = `${ativo.ticker}::${ativo.tipo}`
    const existente = grupos.get(chave)

    if (!existente) {
      grupos.set(chave, { ...ativo })
      continue
    }

    existente.quantidade += ativo.quantidade
    existente.valorTotal += ativo.valorTotal
    existente.totalInvestido += ativo.totalInvestido
    existente.lucro += ativo.lucro
    // Preço de mercado é o mesmo em todos os lotes do ticker; mantém o mais recente não-zero
    existente.preco = ativo.preco || existente.preco

    if ((!existente.nome || existente.nome === existente.ticker) && ativo.nome) {
      existente.nome = ativo.nome
    }
  }

  return Array.from(grupos.values()).map((g) => {
    const variacaoAgregada = g.totalInvestido > 0 ? (g.lucro / g.totalInvestido) * 100 : 0
    return {
      ...g,
      variacao: variacaoAgregada,
    }
  })
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

        const listaBruta = Array.isArray(data.assets) ? data.assets.map(normalizarAtivo) : []
        const lista = agruparPorTicker(listaBruta)
        // Ordena por valor de mercado decrescente — maior posição primeiro
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
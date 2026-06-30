import type { Transaction } from "@/lib/types"

/**
 * O backend (main.py / carteira_service) retorna o campo `type` das
 * transações em português (ex: "compra", "venda"), mas o tipo `Transaction`
 * do frontend (@/lib/types) espera valores em inglês:
 * 'buy' | 'sell' | 'dividend' | 'deposit' | 'withdraw'.
 *
 * Essa função normaliza qualquer transação bruta vinda da API para o
 * shape que os componentes já esperam, sem precisar mudar o backend.
 * Cobre os valores confirmados (compra/venda) e os prováveis equivalentes
 * dos outros tipos, com fallback seguro para não quebrar o render.
 */
const MAPA_TIPO_TRANSACAO: Record<string, Transaction["type"]> = {
  compra: "buy",
  buy: "buy",
  venda: "sell",
  sell: "sell",
  dividendo: "dividend",
  dividend: "dividend",
  proventos: "dividend",
  deposito: "deposit",
  depósito: "deposit",
  deposit: "deposit",
  aporte: "deposit",
  retirada: "withdraw",
  resgate: "withdraw",
  withdraw: "withdraw",
  saque: "withdraw",
}

export function normalizarTipoTransacao(tipoRaw: unknown): Transaction["type"] {
  if (typeof tipoRaw !== "string") return "buy"
  const chave = tipoRaw.trim().toLowerCase()
  return MAPA_TIPO_TRANSACAO[chave] ?? "buy"
}

/**
 * Normaliza um objeto de transação bruto vindo da API (campos podem vir
 * com nomes diferentes / tipo em português) para o shape `Transaction`
 * usado pelos componentes do dashboard.
 */
export function normalizarTransacao(raw: Record<string, unknown>): Transaction {
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
    return undefined
  }

  const status = getStr("status") ?? "success"

  return {
    id: getStr("id") ?? String(Math.random()),
    type: normalizarTipoTransacao(raw["type"]),
    ticker: getStr("ticker"),
    assetType: getStr("assetType", "type_ativo") as Transaction["assetType"],
    category: getStr("category", "categoria") as Transaction["category"],
    amount: getNum("amount", "valor"),
    quantity: getNum("quantity", "quantidade") || undefined,
    price: getNum("price", "preco") || undefined,
    date: getStr("date", "data") ?? new Date().toISOString(),
    status: (status === "success" || status === "pending" || status === "failed"
      ? status
      : "success") as Transaction["status"],
  }
}
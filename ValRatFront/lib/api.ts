const API_URL =
  "http://127.0.0.1:8000"

import type {
  PortfolioData
} from './types'

export const fetchPortfolioData =
  async (): Promise<PortfolioData> => {

    const response =
      await fetch(
        `${API_URL}/carteira`
      )

    if (!response.ok) {

      throw new Error(
        "Erro ao buscar carteira"
      )
    }

    return response.json()
  }

export const deletarCompra =
  async (id: string) => {

    const response =
      await fetch(
        `${API_URL}/compras/${id}`,
        {
          method: "DELETE"
        }
      )

    if (!response.ok) {

      throw new Error(
        "Erro ao deletar compra"
      )
    }

    return response.json()
  }

export const cadastrarCompra = async (
  compra: {
    tipo: string
    ticker: string
    data: string
    quantidade: number
  }
) => {

  const response = await fetch(
    `${API_URL}/compras`,
    {
      method: "POST",

      headers: {
        "Content-Type": "application/json"
      },

      body: JSON.stringify(compra)
    }
  )

  if (!response.ok) {

    throw new Error(
      "Erro ao cadastrar compra"
    )
  }

  return response.json()
}

export async function fetchHistorico() {

  const response =
    await fetch(
      `${API_URL}/historico`
    )

  if (!response.ok) {

    throw new Error(
      'Erro ao buscar histórico'
    )
  }

  return response.json()
}

export async function fetchBenchmarks() {

  const response =
    await fetch(
      `${API_URL}/benchmark`
    )

  if (!response.ok) {

    throw new Error(
      'Erro ao buscar benchmarks'
    )
  }

  return response.json()
}

export async function fetchHistoricoAtivo(
  ticker: string
) {

  const response = await fetch(

    `${API_URL}/ativos/${ticker}/historico`
  )

  if (!response.ok) {

    throw new Error(
      'Erro ao buscar histórico'
    )
  }

  return response.json()
}
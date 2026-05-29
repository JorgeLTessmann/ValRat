# services/market/providers/brapi_provider.py

import requests


BASE_URL = "https://brapi.dev/api/quote"


def buscar_ativo_brapi(ticker: str):
    """
    Busca dados de um ativo via BRAPI
    """
    try:
        response = requests.get(
            f"{BASE_URL}/{ticker}",
            timeout=10
        )

        if response.status_code != 200:
            return None

        data = response.json()
        results = data.get("results", [])

        if not results:
            return None

        ativo = results[0]

        return {
            "nome": ativo.get("longName") or ticker,
            "preco_atual": ativo.get("regularMarketPrice"),
            "historico": []
        }

    except Exception:
        return None


# Alias para manter compatibilidade
buscar_cotacao = buscar_ativo_brapi
# services/market/exchange_service.py
"""
Serviço de cotação histórica USD -> BRL via AwesomeAPI.
Fornece a taxa de câmbio do dólar em uma data específica do passado,
fundamental para calcular o custo de aquisição de criptoativos em reais.
"""

import requests
from datetime import date, datetime, timedelta
from typing import Optional

AWESOME_BASE = "https://economia.awesomeapi.com.br/json/daily/USD-BRL"
FALLBACK_RATE = 5.40  # Taxa de fallback caso todas as tentativas falhem


def buscar_taxa_cambio_usd_brl(data: date) -> Optional[float]:
    """
    Busca a cotação histórica do dólar (USD -> BRL) para uma data específica.

    Tenta a data exata e, em caso de feriado/fim de semana (sem cotação),
    recua até encontrar o último dia útil disponível.

    Args:
        data: Data de referência para buscar a cotação.

    Returns:
        Taxa de câmbio (float), ex: 5.40 para R$ 5,40 por dólar.
        Retorna a taxa de fallback caso nenhuma cotação seja encontrada.
    """
    # Tenta os últimos 5 dias para cobrir feriados e fins de semana
    for delta in range(5):
        data_tentativa = data - timedelta(days=delta)
        taxa = _buscar_cotacao_awesomeapi(data_tentativa)
        if taxa is not None:
            return taxa

    print(f"[CÂMBIO AVISO] Nenhuma cotação encontrada para {data}. Usando fallback: {FALLBACK_RATE}")
    return FALLBACK_RATE


def buscar_taxa_cambio_atual() -> float:
    """
    Busca a cotação atual do dólar (USD -> BRL).

    Returns:
        Taxa de câmbio atual (float) ou fallback em caso de erro.
    """
    taxa = _buscar_cotacao_awesomeapi(date.today())
    if taxa is not None:
        return taxa

    # Tenta os 3 dias anteriores (fim de semana/feriado)
    for delta in range(1, 4):
        taxa = _buscar_cotacao_awesomeapi(date.today() - timedelta(days=delta))
        if taxa is not None:
            return taxa

    return FALLBACK_RATE


def _buscar_cotacao_awesomeapi(data: date) -> Optional[float]:
    """
    Busca internamente a cotação USD-BRL na AwesomeAPI para a data informada.

    Args:
        data: Data no formato date object.

    Returns:
        Valor do bid (compra) do dólar na data, ou None se não encontrado.
    """
    try:
        # A AwesomeAPI aceita datas no formato YYYYMMDD
        data_str = data.strftime("%Y%m%d")
        url = f"{AWESOME_BASE}/?start_date={data_str}&end_date={data_str}"

        resp = requests.get(url, timeout=10)
        if resp.status_code != 200:
            return None

        dados = resp.json()
        if not dados:
            return None

        # Retorna a taxa de compra (bid) do primeiro resultado
        taxa = float(dados[0].get("bid", 0))
        if taxa > 0:
            return taxa

        return None

    except Exception as e:
        print(f"[CÂMBIO ERRO] Falha ao buscar cotação AwesomeAPI para {data}: {e}")
        return None

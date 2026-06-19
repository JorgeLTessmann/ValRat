"""
SERVIÇO DE BENCHMARK

Função: Centralizar o acesso aos principais indicadores de mercado
(CDI, SELIC, IPCA, IBOV) usados como referência para comparar
o rendimento da carteira.

Todos os dados vêm de APIs externas REAIS:
- BrasilAPI: taxas CDI, SELIC, IPCA
- BRAPI: histórico e variação do IBOV

Nenhum dado é mockado ou inventado.
"""

from services.market.indicadores_service import (
    get_cdi_atual,
    get_selic_atual,
    get_ipca_atual
)
from services.brapi_service import buscar_historico_ibov


def get_benchmarks():
    """
    Retorna todos os benchmarks em um único dicionário.
    Usado pelo front-end para exibir indicadores na dashboard.
    """
    
    cdi = get_cdi_atual()
    selic = get_selic_atual()
    ipca = get_ipca_atual()
    ibov = buscar_historico_ibov()
    
    ibov_percentual = None
    if ibov:
        ibov_percentual = ibov.get("regularMarketChangePercent")
    
    return {
        "cdi": cdi / 100 if cdi else None,
        "selic": selic / 100 if selic else None,
        "ipca": ipca / 100 if ipca else None,
        "ibov": ibov_percentual / 100 if ibov_percentual else None
    }


def get_cdi_benchmark():
    """Retorna a taxa CDI atual real"""
    taxa = get_cdi_atual()
    return taxa / 100 if taxa else None


def get_selic_benchmark():
    """Retorna a taxa SELIC atual real"""
    taxa = get_selic_atual()
    return taxa / 100 if taxa else None


def get_ipca_benchmark():
    """Retorna a taxa IPCA atual real"""
    taxa = get_ipca_atual()
    return taxa / 100 if taxa else None


def get_ibov_benchmark():
    """Retorna a variação do IBOV real"""
    ibov = buscar_historico_ibov()
    if ibov:
        return ibov.get("regularMarketChangePercent", 0) / 100
    return None 
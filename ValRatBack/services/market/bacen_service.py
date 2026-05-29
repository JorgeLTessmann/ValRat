# services/market/bacen_service.py

from services.market.brasilapi_service import (
    buscar_taxa_selic,
    buscar_taxa_cdi,
    buscar_taxa_ipca
)


# =========================
# DEPRECATED - Use brasilapi_service.py
# =========================

def get_cdi_anual():
    """
    DEPRECATED: Use buscar_taxa_cdi() do brasilapi_service
    """
    taxa = buscar_taxa_cdi()
    if taxa:
        return taxa / 100
    return None


def get_selic_anual():
    """
    DEPRECATED: Use buscar_taxa_selic() do brasilapi_service
    """
    taxa = buscar_taxa_selic()
    if taxa:
        return taxa / 100
    return None


def get_ipca_anual():
    """
    DEPRECATED: Use buscar_taxa_ipca() do brasilapi_service
    """
    taxa = buscar_taxa_ipca()
    if taxa:
        return taxa / 100
    return None


# Mantém a função original por compatibilidade
def buscar_serie_bacen(codigo: int, data_inicial: str = "01/01/2024"):
    """
    DEPRECATED: Prefira usar BrasilAPI
    """
    return []
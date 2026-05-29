from services.market.brasilapi_service import (
    buscar_taxa_cdi,
    buscar_taxa_selic,
    buscar_taxa_ipca
)
from constants.asset_types import CDI, SELIC, IPCA, PRE


def buscar_taxa_indexador(indexador: str) -> float | None:
    """
    Busca a taxa atual do indexador via BrasilAPI.
    """
    indexador = indexador.lower()

    if indexador == CDI:
        taxa = buscar_taxa_cdi()
        if taxa:
            return taxa / 100
        return None

    if indexador == SELIC:
        taxa = buscar_taxa_selic()
        if taxa:
            return taxa / 100
        return None

    if indexador == IPCA:
        taxa = buscar_taxa_ipca()
        if taxa:
            return taxa / 100
        return None

    if indexador == PRE:
        return None

    return None
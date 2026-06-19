# services/renda_fixa/indexadores_service.py

from datetime import date
from services.market.indicadores_service import (
    buscar_taxa_cdi, 
    buscar_taxa_selic, 
    buscar_taxa_ipca
)
from constants.asset_types import CDI, SELIC, IPCA, PRE


def buscar_taxa_indexador(indexador: str, data_referencia: date = None) -> float | None:
    indexador = indexador.lower()
    
    if indexador == CDI.lower():
        taxa = buscar_taxa_cdi()
        return taxa / 100 if taxa else None

    if indexador == SELIC.lower():
        taxa = buscar_taxa_selic()
        return taxa / 100 if taxa else None

    if indexador == IPCA.lower():
        taxa = buscar_taxa_ipca()
        return taxa / 100 if taxa else None

    if indexador == PRE.lower():
        return None

    return None
# services/renda_fixa/indexadores_service.py

from datetime import date
from services.market.brasilapi_service import buscar_taxa_cdi, buscar_taxa_selic, buscar_taxa_ipca
from services.market.historical_service import buscar_cdi_historico
from constants.asset_types import CDI, SELIC, IPCA, PRE

def buscar_taxa_indexador(indexador: str, data_referencia: date = None) -> float | None:
    indexador = indexador.lower()
    
    if indexador == CDI:
        if data_referencia:
            # Tenta buscar histórico primeiro
            taxa = buscar_cdi_historico(data_referencia)
            if taxa:
                return taxa
        # Fallback para taxa atual
        taxa = buscar_taxa_cdi()
        return taxa / 100 if taxa else None

    if indexador == SELIC:
        taxa = buscar_taxa_selic()
        return taxa / 100 if taxa else None

    if indexador == IPCA:
        taxa = buscar_taxa_ipca()
        return taxa / 100 if taxa else None

    if indexador == PRE:
        return None

    return None
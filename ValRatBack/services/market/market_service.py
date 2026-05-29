# services/market/market_service.py

from services.market.providers.brapi_provider import (
    buscar_ativo_brapi
)

from services.market.brasilapi_service import (
    buscar_taxa_cdi,
    buscar_taxa_selic,
    buscar_taxa_ipca
)

from services.market.sync.atualizar_acoes import (
    atualizar_acoes
)

from services.analytics.snapshot_service import (
    salvar_snapshot_diario
)


# =========================
# RENDA VARIÁVEL
# =========================

def get_stock_data(ticker: str):
    return buscar_ativo_brapi(ticker)


# =========================
# INDICADORES (via BrasilAPI)
# =========================

def get_cdi():
    taxa = buscar_taxa_cdi()
    if taxa:
        return taxa / 100
    return None


def get_selic():
    taxa = buscar_taxa_selic()
    if taxa:
        return taxa / 100
    return None


def get_ipca():
    taxa = buscar_taxa_ipca()
    if taxa:
        return taxa / 100
    return None


# =========================
# MERCADO
# =========================

def atualizar_mercado():
    atualizar_acoes()
    salvar_snapshot_diario()
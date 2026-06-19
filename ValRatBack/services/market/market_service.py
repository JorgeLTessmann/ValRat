
from services.market.providers.brapi_provider import buscar_ativo_brapi

from services.market.indicadores_service import (
    get_cdi_atual,
    get_selic_atual,
    get_ipca_atual
)

from services.market.sync.atualizar_acoes import atualizar_acoes
from services.analytics.snapshot_service import salvar_snapshot_diario


# =========================
# RENDA VARIÁVEL
# =========================

def get_stock_data(ticker: str):
    return buscar_ativo_brapi(ticker)


# =========================
# INDICADORES
# =========================

def get_cdi():
    return get_cdi_atual()


def get_selic():
    return get_selic_atual()


def get_ipca():
    return get_ipca_atual()


# =========================
# MERCADO
# =========================

def atualizar_mercado():
    atualizar_acoes()
    salvar_snapshot_diario()
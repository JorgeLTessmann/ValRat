# services/assets/asset_resolver_service.py

from services.market.providers.brapi_provider import (
    buscar_ativo_brapi
)

from services.assets.asset_catalog_service import (
    buscar_ativo_catalogo
)

from constants.asset_types import (
    RENDA_FIXA_TYPES,
    RENDA_VARIAVEL_TYPES
)


def resolver_ativo(
    ticker: str,
    tipo: str = None
):

    ticker = ticker.strip().upper()

    # =========================
    # SE NÃO TEM TIPO, BUSCA NO CATÁLOGO
    # =========================

    if tipo is None:

        catalogo = buscar_ativo_catalogo(
            ticker
        )

        if catalogo:

            tipo = catalogo.tipo

    # =========================
    # RENDA VARIÁVEL
    # =========================

    if tipo in RENDA_VARIAVEL_TYPES:

        ativo = buscar_ativo_brapi(
            ticker
        )

        if not ativo:

            return None

        return {

            "codigo": ticker,

            "nome": ativo["nome"],

            "tipo": tipo,

            "fonte": "brapi",

            "preco_atual":
                ativo["preco_atual"],

            "historico":
                ativo["historico"]
        }

    # =========================
    # RENDA FIXA
    # =========================

    if tipo in RENDA_FIXA_TYPES:

        return {

            "codigo": ticker,

            "nome": ticker,

            "tipo": tipo,

            "fonte": "manual",

            "preco_atual": 1,

            "historico": []
        }

    return None
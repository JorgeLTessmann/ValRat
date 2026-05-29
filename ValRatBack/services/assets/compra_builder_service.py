from utils.date_utils import (
    normalizar_data_compra
)

from utils.market_utils import (
    buscar_preco_por_data
)

from constants.asset_types import (
    RENDA_VARIAVEL_TYPES
)


def montar_dados_compra(

    ativo,
    tipo,
    ticker,
    quantidade,
    plataforma,
    data_compra,
    valor_investido=None,
    taxa=None,
    indexador=None,
    data_vencimento=None
):

    data_formatada = normalizar_data_compra(
        data_compra
    )

    # =========================
    # RENDA VARIÁVEL
    # =========================

    if tipo in RENDA_VARIAVEL_TYPES:

        preco_compra = buscar_preco_por_data(

            ativo["historico"],
            data_formatada
        )

        if preco_compra is None:

            return None

        valor_investido = (
            quantidade *
            preco_compra
        )

    # =========================
    # RENDA FIXA
    # =========================

    else:

        preco_compra = 1

        quantidade = 1

    return {

        "ticker": ticker,

        "nome": ativo["nome"],

        "tipo": tipo,

        "plataforma": plataforma,

        "quantidade": quantidade,

        "quantidade_original": quantidade,

        "quantidade_restante": quantidade,

        "preco_compra": preco_compra,

        "valor_investido": valor_investido,

        "valor_atual": valor_investido,

        "taxa": taxa,

        "indexador": indexador,

        "data_vencimento": data_vencimento,

        "data_compra": data_formatada
    }
from services.market.bacen_service import (
    get_cdi_anual
)

from services.brapi_service import (
    buscar_historico_ibov
)


def gerar_comparativo(

    historico
):

    if not historico:

        return []

    cdi_anual = get_cdi_anual()

    ibov = buscar_historico_ibov()

    ibov_percentual = 0

    if ibov:

        ibov_percentual = (
            ibov.get(
                "regularMarketChangePercent"
            ) or 0
        ) / 100

    carteira_inicial = historico[0][
        "value"
    ]

    cdi_acumulado = carteira_inicial

    ibov_acumulado = carteira_inicial

    resultado = []

    dias = len(historico)

    taxa_cdi_dia = (
        (1 + cdi_anual) ** (1 / 252)
    ) - 1

    taxa_ibov_dia = (
        (1 + ibov_percentual) ** (1 / 252)
    ) - 1

    for item in historico:

        cdi_acumulado *= (
            1 + taxa_cdi_dia
        )

        ibov_acumulado *= (
            1 + taxa_ibov_dia
        )

        resultado.append({

            "date":
                item["date"],

            "carteira":
                item["value"],

            "cdi":
                round(
                    cdi_acumulado,
                    2
                ),

            "ibov":
                round(
                    ibov_acumulado,
                    2
                )
        })

    return resultado
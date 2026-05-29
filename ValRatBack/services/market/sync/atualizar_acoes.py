from database import (
    SessionLocal
)

from entities.compra import (
    Compra
)

from services.market.providers.brapi_provider import (
    buscar_cotacao
)


def atualizar_acoes():

    db = SessionLocal()

    compras = (
        db.query(Compra)
        .filter(
            Compra.tipo.in_([
                "acao",
                "etf",
                "fii"
            ])
        )
        .all()
    )

    tickers_processados = {}

    for compra in compras:

        ticker = compra.ticker

        if ticker not in tickers_processados:

            cotacao = buscar_cotacao(
                ticker
            )

            if not cotacao:
                continue

            tickers_processados[ticker] = (
                cotacao
            )

        cotacao = tickers_processados[
            ticker
        ]

        preco_atual = cotacao["preco"]

        valor_atual = (
            compra.quantidade_restante *
            preco_atual
        )

        compra.valor_atual = (
            valor_atual
        )

    db.commit()

    db.close()
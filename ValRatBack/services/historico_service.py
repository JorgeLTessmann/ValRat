from datetime import datetime

from database import SessionLocal

from entities.historico_patrimonio import (
    HistoricoPatrimonio
)

from services.portfolio_service import (
    montar_portfolio
)


def registrar_snapshot():

    db = SessionLocal()

    try:

        portfolio = montar_portfolio()

        snapshot = HistoricoPatrimonio(

            data=datetime.now(),

            patrimonio=portfolio[
                "totalBalance"
            ],

            investido=portfolio[
                "totalInvested"
            ],

            lucro=portfolio[
                "profitLoss"
            ]
        )

        db.add(snapshot)

        db.commit()

    except Exception as e:

        print(
            "Erro ao registrar snapshot:",
            str(e)
        )

        db.rollback()

    finally:

        db.close()
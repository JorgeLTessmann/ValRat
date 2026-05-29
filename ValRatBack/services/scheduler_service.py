from apscheduler.schedulers.background import (
    BackgroundScheduler
)

from services.market.market_service import (
    atualizar_mercado
)


scheduler = BackgroundScheduler()


def iniciar_scheduler():

    if scheduler.running:
        return

    scheduler.add_job(

        atualizar_mercado,

        "interval",

        minutes=5
    )

    scheduler.start()

    print(
        "Scheduler iniciado"
    )
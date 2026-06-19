# services/scheduler_service.py

from apscheduler.schedulers.background import BackgroundScheduler
from services.price_service import atualizar_mercado_lote


scheduler = BackgroundScheduler()


def iniciar_scheduler():
    if scheduler.running:
        return

    scheduler.add_job(
        atualizar_mercado_lote,
        "interval",
        minutes=5
    )

    scheduler.start()
    print("Scheduler iniciado com rotinas unificadas de mercado.")
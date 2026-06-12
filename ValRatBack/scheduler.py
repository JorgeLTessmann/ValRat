from apscheduler.schedulers.background import BackgroundScheduler
from services.analytics.snapshot_service import salvar_snapshot_diario
import time
import threading

def iniciar_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(salvar_snapshot_diario, 'interval', hours=24)
    scheduler.start()
    print("✅ Scheduler iniciado - Snapshot diário agendado")
    return scheduler

# Inicia automaticamente
scheduler = iniciar_scheduler()
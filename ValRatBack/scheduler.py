# scheduler.py

import logging
from apscheduler.schedulers.background import BackgroundScheduler
from services.analytics.snapshot_service import salvar_snapshot_diario

logger = logging.getLogger("scheduler")

def iniciar_scheduler():
    scheduler = BackgroundScheduler()
    
    scheduler.add_job(
        salvar_snapshot_diario, 
        'interval', 
        hours=24,
        id='snapshot_diario_job',
        replace_existing=True
    )
    
    scheduler.start()
    logger.info("✅ Scheduler iniciado - Mapeamento de snapshots diários ativo (24h).")
    return scheduler
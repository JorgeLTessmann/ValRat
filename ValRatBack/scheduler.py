# scheduler.py

import logging
from apscheduler.schedulers.background import BackgroundScheduler
from database import SessionLocal
from entities.usuario import Usuario
from services.analytics.snapshot_service import salvar_snapshot_diario

logger = logging.getLogger("scheduler")

def rodar_snapshots_em_lote():
    logger.info("🎬 Iniciando rotina diária de snapshots em lote...")
    db = SessionLocal()
    try:
        usuarios = db.query(Usuario).all()
        for usuario in usuarios:
            try:
                logger.info(f"📸 Gerando snapshot para o usuário: {usuario.email} (ID: {usuario.id})")
                salvar_snapshot_diario(usuario_id=usuario.id)
            except Exception as e:
                logger.error(f"❌ Erro ao processar snapshot do usuário {usuario.id}: {e}")
    except Exception as e:
        logger.error(f"⚠️ Falha ao ler usuários na rotina do scheduler: {e}")
    finally:
        db.close()
    logger.info("🏁 Rotina diária de snapshots finalizada.")

def iniciar_scheduler():
    scheduler = BackgroundScheduler()
    
    scheduler.add_job(
        rodar_snapshots_em_lote, 
        'interval', 
        hours=24,
        id='snapshot_diario_job',
        replace_existing=True
    )
    
    scheduler.start()
    logger.info("✅ Scheduler iniciado - Mapeamento de snapshots diários ativo (24h).")
    return scheduler
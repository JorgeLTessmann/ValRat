from apscheduler.schedulers.blocking import (
    BlockingScheduler
)

from services.snapshot.snapshot_service import (
    salvar_snapshot
)

scheduler = BlockingScheduler()

scheduler.add_job(

    salvar_snapshot,

    'interval',

    hours=24
)

print(
    "Scheduler iniciado..."
)

scheduler.start()
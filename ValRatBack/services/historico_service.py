# services/historico_service.py

from services.analytics.snapshot_service import salvar_snapshot_diario


def registrar_snapshot(usuario_id: int):
    salvar_snapshot_diario(usuario_id=usuario_id)
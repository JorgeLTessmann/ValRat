# services/historico_service.py

from services.analytics.snapshot_service import salvar_snapshot_diario


def registrar_snapshot():
    salvar_snapshot_diario()
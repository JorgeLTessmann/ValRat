# services/analytics/snapshot_service.py

from datetime import datetime, date
from database import SessionLocal
from entities.historico_patrimonio import HistoricoPatrimonio
from services.portfolio_service import montar_portfolio


def calcular_snapshot_atual(usuario_id: int) -> dict:
    """
    Calcula o patrimônio ATUAL ao vivo, sem gravar no banco.
    Reusado tanto pelo snapshot persistente quanto pelo /historico (ponto do dia).
    """
    portfolio = montar_portfolio(usuario_id=usuario_id, force_refresh=True)

    total_balance = portfolio.get("totalBalance", 0)
    total_invested = portfolio.get("totalInvested", 0)
    profit_loss = portfolio.get("profitLoss", 0)
    percentual = (profit_loss / total_invested) * 100 if total_invested > 0 else 0.0

    return {
        "patrimonio": total_balance,
        "investido": total_invested,
        "lucro": profit_loss,
        "percentual": percentual,
    }


def salvar_snapshot_diario(usuario_id: int):
    """Salva snapshot do patrimônio total isolado por usuário"""
    db = SessionLocal()

    try:
        dados = calcular_snapshot_atual(usuario_id)

        snapshot = HistoricoPatrimonio(
            usuario_id=usuario_id,
            patrimonio=dados["patrimonio"],
            investido=dados["investido"],
            lucro=dados["lucro"],
            percentual=dados["percentual"],
            data=datetime.now()
        )

        db.add(snapshot)
        db.commit()
        print(f"✅ Snapshot salvo para o usuário {usuario_id}: patrimônio R$ {dados['patrimonio']:.2f}")

    except Exception as e:
        print(f"❌ Erro no snapshot do usuário {usuario_id}: {e}")
        db.rollback()
    finally:
        db.close()


def registrar_snapshot(usuario_id: int):
    """Alias para compatibilidade"""
    return salvar_snapshot_diario(usuario_id=usuario_id)
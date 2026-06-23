# services/analytics/snapshot_service.py

from datetime import datetime, date
from dateutil.relativedelta import relativedelta  # pip install python-dateutil, se ainda não tiver
from database import SessionLocal
from entities.historico_patrimonio import HistoricoPatrimonio
from services.portfolio_service import montar_portfolio_em_data, montar_portfolio


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

def recalcular_historico_a_partir_de(usuario_id: int, data_compra_str: str):
    """
    Quando uma compra/aplicação retroativa é cadastrada, apaga os snapshots
    contaminados (gravados como se essa compra não existisse) e regenera
    o histórico mensal a partir da data do ativo até hoje.
    """
    db = SessionLocal()
    try:
        data_inicio = date.fromisoformat(data_compra_str)
        # Normaliza para o dia 1 do mês da compra (granularidade mensal)
        data_inicio = data_inicio.replace(day=1)
        hoje = date.today()

        # 1. Apaga snapshots a partir da data da compra (inclusive)
        db.query(HistoricoPatrimonio).filter(
            HistoricoPatrimonio.usuario_id == usuario_id,
            HistoricoPatrimonio.data >= data_inicio
        ).delete(synchronize_session=False)
        db.commit()

        # 2. Gera a lista de datas (dia 1 de cada mês) entre data_inicio e hoje
        datas_para_recalcular = []
        cursor = data_inicio
        while cursor <= hoje:
            datas_para_recalcular.append(cursor)
            cursor = cursor + relativedelta(months=1)

        # 3. Recalcula e grava um snapshot novo para cada mês
        for data_ponto in datas_para_recalcular:
            portfolio_no_mes = montar_portfolio_em_data(usuario_id, data_ponto)

            snapshot = HistoricoPatrimonio(
                usuario_id=usuario_id,
                patrimonio=portfolio_no_mes["totalBalance"],
                investido=portfolio_no_mes["totalInvested"],
                lucro=portfolio_no_mes["profitLoss"],
                percentual=(
                    portfolio_no_mes["profitLoss"] / portfolio_no_mes["totalInvested"] * 100
                    if portfolio_no_mes["totalInvested"] > 0 else 0.0
                ),
                data=datetime.combine(data_ponto, datetime.min.time())
            )
            db.add(snapshot)

        db.commit()
        print(f"✅ Histórico recalculado para usuário {usuario_id}, a partir de {data_inicio.isoformat()} ({len(datas_para_recalcular)} pontos)")

    except Exception as e:
        print(f"❌ Erro ao recalcular histórico retroativo do usuário {usuario_id}: {e}")
        db.rollback()
    finally:
        db.close()

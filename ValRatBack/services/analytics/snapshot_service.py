import threading
import logging
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

from database import SessionLocal
from entities.historico_patrimonio import HistoricoPatrimonio
from entities.compra import Compra
from entities.renda_fixa import RendaFixa
from services.portfolio_service import montar_portfolio_em_data, montar_portfolio

logger = logging.getLogger(__name__)

# Controle de concorrência em memória (Evita travar o servidor com múltiplos cliques)
_usuarios_recalculando = set()
_lock_recalculo = threading.Lock()

def calcular_snapshot_atual(usuario_id: int) -> dict:
    """Calcula o patrimônio ATUAL ao vivo (real-time)."""
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
    """Gera o ponto do dia atual no banco."""
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
        logger.info(f"✅ Snapshot diário salvo para usuário {usuario_id}")
    except Exception as e:
        logger.error(f"❌ Erro no snapshot diário: {e}")
        db.rollback()
    finally:
        db.close()

def recalcular_historico_incremental(usuario_id: int):
    """
    Refatoração Inteligente: Não apaga o passado.
    Busca o último ponto gerado ou a compra mais antiga, calculando apenas o delta faltante.
    """
    with _lock_recalculo:
        if usuario_id in _usuarios_recalculando:
            logger.info(f"⏭️ Recálculo já rodando para o usuário {usuario_id}. Ignorando chamada duplicada.")
            return
        _usuarios_recalculando.add(usuario_id)

    db = SessionLocal()
    try:
        hoje = date.today()
        
        # 1. Verifica qual o último ponto salvo no banco para este usuário
        ultimo_ponto = db.query(HistoricoPatrimonio)\
            .filter(HistoricoPatrimonio.usuario_id == usuario_id)\
            .order_by(HistoricoPatrimonio.data.desc())\
            .first()

        if ultimo_ponto:
            # Começa a partir do mês seguinte ao último ponto guardado
            if hasattr(ultimo_ponto.data, "date"):
                data_inicio = ultimo_ponto.data.date() + relativedelta(months=1)
            else:
                data_inicio = datetime.strptime(str(ultimo_ponto.data).split(" ")[0], "%Y-%m-%d").date() + relativedelta(months=1)
            data_inicio = data_inicio.replace(day=1)
            logger.info(f"🔄 Histórico existente achado. Calculando novos pontos a partir de: {data_inicio}")
        else:
            # Se o banco está zerado, busca a movimentação mais antiga
            datas_compras = [c.data_compra for c in db.query(Compra).filter(Compra.usuario_id == usuario_id).all() if c.data_compra]
            datas_rf = [a.data_aplicacao for a in db.query(RendaFixa).filter(RendaFixa.usuario_id == usuario_id).all() if a.data_aplicacao]
            todas_as_datas = datas_compras + datas_rf

            if not todas_as_datas:
                logger.warning(f"⚠️ Usuário {usuario_id} não possui nenhum ativo cadastrado.")
                return

            data_inicio = date.fromisoformat(min(todas_as_datas)).replace(day=1)
            logger.info(f"🌱 Nenhum histórico encontrado. Gerando do zero desde a primeira compra: {data_inicio}")

        # 2. Monta a fila de meses que precisam ser calculados
        datas_para_recalcular = []
        cursor = data_inicio
        while cursor <= hoje:
            datas_para_recalcular.append(cursor)
            cursor = cursor + relativedelta(months=1)

        if not datas_para_recalcular:
            logger.info(f"✅ O gráfico já está totalmente atualizado para o usuário {usuario_id}.")
            return

        # 3. Executa o cálculo mensal
        for data_ponto in datas_para_recalcular:
            logger.info(f"📊 Processando ponto histórico para a data: {data_ponto.isoformat()}")
            portfolio_no_mes = montar_portfolio_em_data(usuario_id, data_ponto)

            snapshot = HistoricoPatrimonio(
                usuario_id=usuario_id,
                patrimonio=portfolio_no_mes["totalBalance"],
                investido=portfolio_no_mes["totalInvested"],
                lucro=portfolio_no_mes["profitLoss"],
                percentual=(
                    (portfolio_no_mes["profitLoss"] / portfolio_no_mes["totalInvested"] * 100)
                    if portfolio_no_mes["totalInvested"] > 0 else 0.0
                ),
                data=datetime.combine(data_ponto, datetime.min.time())
            )
            db.add(snapshot)
            db.commit() # Commita ponto a ponto para liberar o banco gradualmente

        logger.info(f"✨ Recálculo concluído com sucesso para o usuário {usuario_id}. {len(datas_para_recalcular)} pontos adicionados.")

    except Exception as e:
        logger.error(f"❌ Erro crítico no recálculo incremental do usuário {usuario_id}: {e}", exc_info=True)
        db.rollback()
    finally:
        db.close()
        with _lock_recalculo:
            _usuarios_recalculando.discard(usuario_id)
# services/analytics/snapshot_service.py

from datetime import datetime
from database import SessionLocal
from entities.historico_patrimonio import HistoricoPatrimonio
from services.portfolio_service import montar_portfolio


def salvar_snapshot_diario(usuario_id: int):  # ← Adicionado parâmetro obrigatório
    """Salva snapshot do patrimônio total isolado por usuário"""
    db = SessionLocal()
    
    try:
        # Força recálculo do portfólio filtrado para este usuário específico
        portfolio = montar_portfolio(usuario_id=usuario_id, force_refresh=True)
        
        total_balance = portfolio.get("totalBalance", 0)
        total_invested = portfolio.get("totalInvested", 0)
        profit_loss = portfolio.get("profitLoss", 0)
        
        # Calcula percentual (evita divisão por zero)
        if total_invested > 0:
            percentual = (profit_loss / total_invested) * 100
        else:
            percentual = 0.0
        
        # Cria a linha histórica informando a qual investidor ela pertence
        snapshot = HistoricoPatrimonio(
            usuario_id=usuario_id,  # ← CRÍTICO: Garante que os gráficos históricos fiquem separados
            patrimonio=total_balance,
            investido=total_invested,
            lucro=profit_loss,
            percentual=percentual,
            data=datetime.now()
        )
        
        db.add(snapshot)
        db.commit()
        print(f"✅ Snapshot salvo para o usuário {usuario_id}: patrimônio R$ {total_balance:.2f}")
        
    except Exception as e:
        print(f"❌ Erro no snapshot do usuário {usuario_id}: {e}")
        db.rollback()
    finally:
        db.close()


def registrar_snapshot(usuario_id: int):  # ← Repassa o parâmetro no alias
    """Alias para compatibilidade"""
    return salvar_snapshot_diario(usuario_id=usuario_id)
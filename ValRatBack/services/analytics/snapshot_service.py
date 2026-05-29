# services/analytics/snapshot_service.py

from datetime import datetime
from database import SessionLocal
from entities.historico_ativo import HistoricoAtivo


def salvar_snapshot_diario():
    """
    Salva snapshot diário do portfólio.
    Importa montar_portfolio dentro da função para evitar circular import.
    """
    
    from services.portfolio_service import montar_portfolio
    
    db = SessionLocal()
    
    try:
        portfolio = montar_portfolio()
        assets = portfolio.get("assets", [])

        agora = datetime.now()

        for asset in assets:
            historico = HistoricoAtivo(
                ticker=asset.get("ticker", ""),
                tipo=asset.get("type", ""),
                preco=asset.get("currentPrice", 0),
                quantidade=asset.get("quantity", 0),
                valor_total=asset.get("currentValue", 0),
                data_snapshot=agora
            )
            db.add(historico)

        db.commit()
        print(f"✅ Snapshot salvo: {len(assets)} ativos")
        
    except Exception as e:
        print(f"❌ Erro ao salvar snapshot: {e}")
        db.rollback()
        
    finally:
        db.close()
# services/portfolio_service.py

import logging
from database import SessionLocal
from entities.compra import Compra
from entities.historico_patrimonio import HistoricoPatrimonio
from entities.transacao import Transacao
from services.portfolio.variable_income import calcular_renda_variavel
from services.portfolio.fixed_income import calcular_renda_fixa_das_compras
# from services.analytics.comparison_service import gerar_comparativo
from services.portfolio.allocation_service import gerar_allocations
from services.cache_service import get_cache, set_cache

logger = logging.getLogger(__name__)


def montar_portfolio(usuario_id: int, force_refresh: bool = False):
    # Geramos uma chave de cache exclusiva para o ID deste usuário
    cache_key = f"portfolio_completo_{usuario_id}"

    if not force_refresh:
        cached = get_cache(cache_key, max_age_seconds=30)
        if cached:
            return cached
    
    db = SessionLocal()

    # CRÍTICO: Filtrando as compras exclusivamente do usuário logado
    compras = db.query(Compra).filter(
        Compra.usuario_id == usuario_id
    ).all()

    logger.info(f"Total de compras no banco para usuario {usuario_id}: {len(compras)}")
    
    compras_variavel = [c for c in compras if c.categoria in ["variavel", "cripto"]]
    compras_fixa = [c for c in compras if c.categoria in ["fixa", "Renda Fixa", None]]
    
    logger.info(f"Compras variável: {len(compras_variavel)}, Compras fixa: {len(compras_fixa)}")

    assets_variavel, balance_variavel, invested_variavel, ir_variavel = calcular_renda_variavel(compras_variavel)
    assets_fixa, balance_fixa, invested_fixa, ir_fixa = calcular_renda_fixa_das_compras(compras_fixa)

    assets = assets_variavel + assets_fixa
    total_balance = balance_variavel + balance_fixa
    total_invested = invested_variavel + invested_fixa
    total_ir = ir_variavel + ir_fixa

    # CRÍTICO: Filtrando as transações do usuário logado
    transacoes_db = db.query(Transacao).filter(
        Transacao.usuario_id == usuario_id
    ).order_by(Transacao.data.desc()).limit(50).all()
    
    transactions = []
    for t in transacoes_db:
        transactions.append({
            "id": str(t.id),
            "type": t.tipo,
            "ticker": t.ticker,
            "amount": t.valor,
            "quantity": t.quantidade,
            "price": t.preco,
            "date": t.data.isoformat(),
            "status": t.status
        })

    # CRÍTICO: Filtrando o histórico de patrimônio do usuário logado
    historico = db.query(HistoricoPatrimonio).filter(
        HistoricoPatrimonio.usuario_id == usuario_id
    ).order_by(HistoricoPatrimonio.data.asc()).all()
    
    historico_formatado = []
    for item in historico:
        historico_formatado.append({
            "date": item.data.strftime("%Y-%m-%d"),
            "value": round(item.patrimonio, 2)
        })

    # comparativo = gerar_comparativo(historico_formatado)
    comparativo = []
    allocations = gerar_allocations(assets=assets, total_balance=total_balance)

    db.close()

    # Evita divisão por zero se for uma conta nova sem aportes
    profit_loss_total = total_balance - total_invested
    percent_change_total = (profit_loss_total / total_invested * 100) if total_invested > 0 else 0

    resultado = {
        "totalBalance": round(total_balance, 2),
        "totalInvested": round(total_invested, 2),
        "profitLoss": round(profit_loss_total, 2),
        "percentChange": round(percent_change_total, 2),
        "totalIr": round(total_ir, 2),
        "assets": assets,
        "transactions": transactions,
        "allocations": allocations,
        "historicalData": historico_formatado,
        "comparisonData": comparativo
    }
    
    # Salva no cache com a chave única do usuário
    set_cache(cache_key, resultado)
    return resultado

def montar_portfolio_resumido(usuario_id: int):
    db = SessionLocal()
    try:
        ultimo = db.query(HistoricoPatrimonio).filter(
            HistoricoPatrimonio.usuario_id == usuario_id
        ).order_by(HistoricoPatrimonio.data.desc()).first()
        
        if ultimo:
            return {
                "totalBalance": float(ultimo.patrimonio) if ultimo.patrimonio is not None else 0.0,
                "totalInvested": float(ultimo.investido) if ultimo.investido is not None else 0.0,
                "profitLoss": float(ultimo.lucro) if ultimo.lucro is not None else 0.0,
                "percentChange": float(ultimo.percentual) if ultimo.percentual is not None else 0.0
            }
        
        compras = db.query(Compra).filter(Compra.usuario_id == usuario_id).all()
        
        if compras:
            compras_variavel = [c for c in compras if c.categoria in ["variavel", "cripto"]]
            compras_fixa = [c for c in compras if c.categoria in ["fixa", "Renda Fixa", None]]
            
            _, balance_var, invested_var, _ = calcular_renda_variavel(compras_variavel)
            _, balance_fixa, invested_fixa, _ = calcular_renda_fixa_das_compras(compras_fixa)
            
            total_balance = balance_var + balance_fixa
            total_invested = invested_var + invested_fixa
            profit_loss = total_balance - total_invested
            percent_change = (profit_loss / total_invested * 100) if total_invested > 0 else 0.0
            
            return {
                "totalBalance": round(total_balance, 2),
                "totalInvested": round(total_invested, 2),
                "profitLoss": round(profit_loss, 2),
                "percentChange": round(percent_change, 2)
            }
    except Exception as e:
        logger.error(f"Erro ao buscar ultimo historico de patrimonio para o usuario {usuario_id}: {e}", exc_info=True)
    finally:
        db.close()
    
    return {
        "totalBalance": 0.0,
        "totalInvested": 0.0,
        "profitLoss": 0.0,
        "percentChange": 0.0
    }
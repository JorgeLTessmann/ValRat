from database import SessionLocal

from entities.compra import Compra
from entities.renda_fixa import RendaFixa
from entities.historico_patrimonio import HistoricoPatrimonio

from services.portfolio.variable_income import calcular_renda_variavel
from services.portfolio.fixed_income import calcular_renda_fixa
from services.analytics.comparison_service import gerar_comparativo
from services.portfolio.allocation_service import gerar_allocations


def montar_portfolio():
    db = SessionLocal()

    compras = (
        db.query(Compra)
        .filter(Compra.quantidade_restante > 0)
        .all()
    )

    rendas_fixas = (
        db.query(RendaFixa)
        .all()
    )

    historico = (
        db.query(HistoricoPatrimonio)
        .order_by(HistoricoPatrimonio.data.asc())
        .all()
    )

    # =========================
    # RENDA VARIÁVEL
    # =========================
    assets_variavel, balance_variavel, invested_variavel = (
        calcular_renda_variavel(compras)
    )

    # =========================
    # RENDA FIXA
    # =========================
    assets_fixa, balance_fixa, invested_fixa = (
        calcular_renda_fixa(rendas_fixas)
    )

    # =========================
    # ASSETS GERAIS
    # =========================
    assets = []
    assets.extend(assets_variavel)
    assets.extend(assets_fixa)

    total_balance = balance_variavel + balance_fixa
    total_invested = invested_variavel + invested_fixa

    transactions = []

    # =========================
    # HISTÓRICO
    # =========================
    historico_formatado = []

    for item in historico:
        historico_formatado.append({
            "date": item.data.strftime("%Y-%m-%d"),
            "value": round(item.patrimonio, 2)
        })

    # =========================
    # COMPARATIVO
    # =========================
    comparativo = gerar_comparativo(historico_formatado)

    # =========================
    # ALLOCATIONS
    # =========================
    allocations = gerar_allocations(
        assets=assets,
        total_balance=total_balance
    )

    db.close()

    # =========================
    # RESULTADO GERAL
    # =========================
    profit_loss_total = total_balance - total_invested
    percent_change_total = (
        (profit_loss_total / total_invested) * 100
        if total_invested > 0
        else 0
    )

    return {
        "totalBalance": round(total_balance, 2),
        "totalInvested": round(total_invested, 2),
        "profitLoss": round(profit_loss_total, 2),
        "percentChange": round(percent_change_total, 2),
        "assets": assets,
        "transactions": transactions,
        "allocations": allocations,
        "historicalData": historico_formatado,
        "comparisonData": comparativo
    }
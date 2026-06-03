# services/portfolio/variable_income.py

from datetime import date
from services.price_service import buscar_preco, calcular_rentabilidade
from services.imposto_service import calcular_ir


def calcular_renda_variavel(compras, data_referencia: date = None):
    """
    Retorna cada compra como um asset individual, já com IR.
    """
    if data_referencia is None:
        data_referencia = date.today()
    
    assets = []
    total_balance = 0
    total_invested = 0
    total_ir = 0

    for compra in compras:
        tipo_busca = "acao"
        if compra.categoria == "cripto":
            tipo_busca = "cripto"
        
        preco_atual = buscar_preco(tipo_busca, compra.ticker, None)
        
        if preco_atual is None:
            continue
        
        rent = calcular_rentabilidade(
            tipo=tipo_busca,
            preco_compra=compra.preco_compra,
            quantidade=compra.quantidade_restante,
            preco_atual=preco_atual
        )
        
        lucro_bruto = rent["lucro"]
        
        # Calcula IR (para ações, alíquota padrão de 15% sobre lucro)
        data_compra = date.fromisoformat(compra.data_compra)
        ir = calcular_ir(
            tipo_ativo=compra.tipo or "acao",
            data_compra=data_compra,
            data_venda=data_referencia,
            lucro=lucro_bruto
        )
        
        valor_liquido = rent["valor_atual"] - ir
        lucro_liquido = valor_liquido - rent["valor_investido"]
        percentual_liquido = (lucro_liquido / rent["valor_investido"] * 100) if rent["valor_investido"] > 0 else 0

        total_balance += valor_liquido
        total_invested += rent["valor_investido"]
        total_ir += ir
        
        assets.append({
            "id": f"v_{compra.id}",
            "ticker": compra.ticker,
            "name": compra.nome or compra.ticker,
            "type": compra.categoria,
            "quantity": compra.quantidade_restante,
            "averagePrice": round(compra.preco_compra, 2),
            "currentPrice": round(preco_atual, 2),
            "totalInvested": rent["valor_investido"],
            "currentValue": round(valor_liquido, 2),
            "grossValue": rent["valor_atual"],
            "ir": round(ir, 2),
            "profitLoss": round(lucro_liquido, 2),
            "percentChange": round(percentual_liquido, 2),
            "plataforma": compra.plataforma,
            "data_compra": compra.data_compra
        })
    
    return assets, total_balance, total_invested, total_ir
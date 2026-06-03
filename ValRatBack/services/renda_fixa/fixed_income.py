# services/portfolio/fixed_income.py

from services.price_service import calcular_valor_atual_fixa


def calcular_renda_fixa(rendas_fixas):
    assets = []
    total_balance = 0
    total_invested = 0

    for ativo in rendas_fixas:
        print(f"📊 Processando renda fixa: {ativo.nome}")
        print(f"   Valor inicial: {ativo.valor_aplicado}")
        print(f"   Taxa: {ativo.taxa}")
        print(f"   Indexador: {ativo.indexador}")
        print(f"   Data aplicação: {ativo.data_aplicacao}")
        
        valor_atual = calcular_valor_atual_fixa(
            valor_inicial=ativo.valor_aplicado,
            taxa_percentual=ativo.taxa,
            indexador=ativo.indexador,
            data_aplicacao_str=ativo.data_aplicacao
        )
        
        print(f"   Valor atual calculado: {valor_atual}")
        
        lucro = valor_atual - ativo.valor_aplicado
        percentual = (lucro / ativo.valor_aplicado) * 100 if ativo.valor_aplicado > 0 else 0

        total_balance += valor_atual
        total_invested += ativo.valor_aplicado

        assets.append({
            "id": f"f_{ativo.id}",
            "ticker": ativo.nome,
            "name": ativo.nome,
            "type": "fixa",
            "quantity": 1,
            "averagePrice": round(ativo.valor_aplicado, 2),
            "currentPrice": round(valor_atual, 2),
            "totalInvested": round(ativo.valor_aplicado, 2),
            "currentValue": round(valor_atual, 2),
            "profitLoss": round(lucro, 2),
            "percentChange": round(percentual, 2),
            "plataforma": ativo.plataforma,
            "data_compra": ativo.data_aplicacao
        })

    return assets, total_balance, total_invested


def calcular_renda_fixa_das_compras(compras_fixa):
    assets = []
    total_balance = 0
    total_invested = 0

    for compra in compras_fixa:
        valor_atual = calcular_valor_atual_fixa(
            valor_inicial=compra.valor_investido,
            taxa_percentual=compra.taxa,
            indexador=compra.indexador,
            data_aplicacao_str=compra.data_compra,
            data_final_str=None
        )
        lucro = valor_atual - compra.valor_investido
        percentual = (lucro / compra.valor_investido * 100) if compra.valor_investido > 0 else 0

        total_balance += valor_atual
        total_invested += compra.valor_investido

        assets.append({
            "id": f"f_{compra.id}",
            "ticker": compra.ticker,
            "name": compra.nome or compra.ticker,
            "type": compra.tipo or "fixa",
            "quantity": compra.quantidade_restante,
            "averagePrice": round(compra.valor_investido / compra.quantidade_original, 2) if compra.quantidade_original else 0,
            "currentPrice": round(valor_atual / compra.quantidade_restante, 2) if compra.quantidade_restante else 0,
            "totalInvested": round(compra.valor_investido, 2),
            "currentValue": round(valor_atual, 2),
            "profitLoss": round(lucro, 2),
            "percentChange": round(percentual, 2),
            "plataforma": compra.plataforma,
            "data_compra": compra.data_compra
        })

    return assets, total_balance, total_invested
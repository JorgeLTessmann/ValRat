# services/portfolio/fixed_income.py

from services.renda_fixa.calculadora_renda_fixa import calcular_valor_renda_fixa


def calcular_renda_fixa(rendas_fixas):
    """
    Calcula posição atual de cada compra de renda fixa individualmente
    """
    assets = []
    total_balance = 0
    total_invested = 0

    for ativo in rendas_fixas:
        
        # Calcula valor atual baseado na data da compra
        valor_atual = calcular_valor_renda_fixa(
            valor_inicial=ativo.valor_aplicado,
            taxa=ativo.taxa,
            indexador=ativo.indexador,
            data_compra=ativo.data_aplicacao,  # ← data específica da compra
            data_final=None
        )

        lucro = valor_atual - ativo.valor_aplicado

        percentual = (
            (lucro / ativo.valor_aplicado) * 100
            if ativo.valor_aplicado > 0
            else 0
        )

        total_balance += valor_atual
        total_invested += ativo.valor_aplicado

        assets.append({
            "id": ativo.id,
            "ticker": ativo.nome,
            "name": ativo.nome,
            "type": ativo.tipo,
            "quantity": 1,
            "averagePrice": round(ativo.valor_aplicado, 2),
            "currentPrice": round(valor_atual, 2),
            "totalInvested": round(ativo.valor_aplicado, 2),
            "currentValue": round(valor_atual, 2),
            "profitLoss": round(lucro, 2),
            "percentChange": round(percentual, 2),
            "plataforma": ativo.plataforma,
            "data_compra": ativo.data_aplicacao  # ← adiciona data para referência
        })

    return assets, total_balance, total_invested
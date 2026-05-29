from services.price_service import calcular_valor_atual_fixa


def calcular_renda_fixa(rendas_fixas):
    """
    Retorna cada ativo de renda fixa como um asset individual.
    Calcula valor atual baseado no indexador e data de aplicação.
    """
    assets = []
    total_balance = 0
    total_invested = 0

    for ativo in rendas_fixas:
        
        valor_atual = calcular_valor_atual_fixa(
            valor_inicial=ativo.valor_aplicado,
            taxa_percentual=ativo.taxa,
            indexador=ativo.indexador,
            data_aplicacao_str=ativo.data_aplicacao
        )

        lucro = valor_atual - ativo.valor_aplicado
        percentual = (lucro / ativo.valor_aplicado) * 100 if ativo.valor_aplicado > 0 else 0

        total_balance += valor_atual
        total_invested += ativo.valor_aplicado

        assets.append({
            "id": f"f_{ativo.id}",
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
            "data_compra": ativo.data_aplicacao
        })

    return assets, total_balance, total_invested
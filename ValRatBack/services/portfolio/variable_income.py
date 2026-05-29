from services.price_service import buscar_preco, calcular_rentabilidade


def calcular_renda_variavel(compras):
    """
    Retorna cada compra como um asset individual.
    NÃO AGREGA POR TICKER.
    Busca preço atual via BRAPI para cada ativo.
    """
    assets = []
    total_balance = 0
    total_invested = 0

    for compra in compras:
        
        # Busca preço atual do ativo
        preco_atual = buscar_preco(compra.tipo, compra.ticker, None)
        
        if preco_atual is None:
            # Se não conseguir preço atual, pula esta compra
            continue
        
        # Calcula rentabilidade
        rent = calcular_rentabilidade(
            tipo=compra.tipo,
            preco_compra=compra.preco_compra,
            quantidade=compra.quantidade_restante,
            preco_atual=preco_atual
        )
        
        quantidade = compra.quantidade_restante
        preco_compra = compra.preco_compra
        
        total_balance += rent["valor_atual"]
        total_invested += rent["valor_investido"]
        
        assets.append({
            "id": f"v_{compra.id}",
            "ticker": compra.ticker,
            "name": compra.nome,
            "type": compra.tipo,
            "quantity": quantidade,
            "averagePrice": round(preco_compra, 2),
            "currentPrice": round(preco_atual, 2),
            "totalInvested": rent["valor_investido"],
            "currentValue": rent["valor_atual"],
            "profitLoss": rent["lucro"],
            "percentChange": rent["percentual"],
            "plataforma": compra.plataforma,
            "data_compra": compra.data_compra
        })
    
    return assets, total_balance, total_invested
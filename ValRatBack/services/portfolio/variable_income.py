# services/portfolio/variable_income.py

import logging
from datetime import date
from services.market.cotacao_cache_service import buscar_preco_com_cache
from services.price_service import calcular_rentabilidade
from services.imposto_service import calcular_ir

logger = logging.getLogger(__name__)


def calcular_renda_variavel(compras, data_referencia: date = None):
    if data_referencia is None:
        data_referencia = date.today()

    # Só passamos uma data explícita para buscar_preco() quando o cálculo
    # NÃO é para hoje — preserva o comportamento atual (preço em tempo real)
    # no caminho mais usado, e usa preço histórico só quando recalculando o passado.
    eh_recalculo_retroativo = data_referencia < date.today()
    data_busca_str = data_referencia.isoformat() if eh_recalculo_retroativo else None

    logger.info(
        f"Calculando renda variável para {len(compras)} compras "
        f"(referência: {data_referencia.isoformat()}, histórico: {eh_recalculo_retroativo})"
    )

    assets = []
    total_balance = 0
    total_invested = 0
    total_ir = 0

    for compra in compras:
        # Ignora ativos que ainda não existiam na data de referência
        data_compra = date.fromisoformat(compra.data_compra)
        if data_compra > data_referencia:
            continue

        tipo_busca = "cripto" if compra.categoria == "cripto" else "acao"
        preco_atual = buscar_preco_com_cache(tipo_busca, compra.ticker, data_busca_str)
        if preco_atual is None:
            logger.warning(
                f"❌ Preço não encontrado para {compra.ticker} (tipo: {tipo_busca}, data: {data_busca_str or 'atual'})"
            )
            continue

        rent = calcular_rentabilidade(
            tipo=tipo_busca,
            preco_compra=compra.preco_compra,
            quantidade=compra.quantidade_restante,
            preco_atual=preco_atual
        )

        lucro_bruto = rent["lucro"]

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
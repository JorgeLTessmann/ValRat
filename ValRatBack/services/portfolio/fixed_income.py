# services/portfolio/fixed_income.py

import logging
from datetime import date
from services.price_service import calcular_valor_atual_fixa
from services.imposto_service import calcular_ir

logger = logging.getLogger(__name__)


def calcular_renda_fixa_das_compras(compras_fixa, data_referencia: date = None):
    if data_referencia is None:
        data_referencia = date.today()
    
    logger.info(f"Calculando renda fixa para {len(compras_fixa)} compras")
    
    assets = []
    total_balance = 0.0
    total_invested = 0.0
    total_ir = 0.0

    for compra in compras_fixa:
        valor_bruto = calcular_valor_atual_fixa(
            valor_inicial=compra.valor_investido,
            taxa_percentual=compra.taxa_contratada,
            indexador=compra.indexador,
            data_aplicacao_str=compra.data_compra
        )
        
        lucro_bruto = valor_bruto - compra.valor_investido
        data_compra = date.fromisoformat(compra.data_compra)
        
        ir = calcular_ir(
            tipo_ativo=compra.tipo_renda_fixa or "cdb",
            data_compra=data_compra,
            data_venda=data_referencia,
            lucro=lucro_bruto
        )
        
        valor_liquido = valor_bruto - ir
        lucro_liquido = valor_liquido - compra.valor_investido
        percentual = (lucro_liquido / compra.valor_investido * 100) if compra.valor_investido > 0 else 0

        total_balance += valor_liquido
        total_invested += compra.valor_investido
        total_ir += ir

        tipo_exibicao = compra.tipo_renda_fixa or "cdb"
        labels = {"cdb": "CDB", "lci": "LCI", "lca": "LCA", "tesouro": "Tesouro"}
        tipo_label = labels.get(tipo_exibicao, "Renda Fixa")

        assets.append({
            "id": f"f_{compra.id}",
            "ticker": compra.ticker,
            "name": compra.nome_aplicacao or compra.ticker,
            "type": tipo_exibicao,
            "type_label": tipo_label,
            "quantity": compra.quantidade_restante,
            "averagePrice": round(compra.valor_investido / compra.quantidade_original, 2) if compra.quantidade_original else 0,
            "currentPrice": round(valor_liquido / compra.quantidade_restante, 2) if compra.quantidade_restante else 0,
            "totalInvested": round(compra.valor_investido, 2),
            "currentValue": round(valor_liquido, 2),
            "grossValue": round(valor_bruto, 2),
            "ir": round(ir, 2),
            "profitLoss": round(lucro_liquido, 2),
            "percentChange": round(percentual, 2),
            "plataforma": compra.plataforma,
            "data_compra": compra.data_compra
        })

    return assets, total_balance, total_invested, total_ir
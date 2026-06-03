# services/imposto_service.py

from datetime import date
from services.imposto_config_service import (
    get_aliquota_ir_renda_fixa,
    is_ativo_isento,
    get_aliquota_acao,
    get_aliquota_cripto,
    get_aliquota_fundo_investimento
)


def calcular_ir(
    tipo_ativo: str,
    data_compra: date,
    data_venda: date,
    lucro: float,
    valor_vendido_mes: float = 0,
    is_day_trade: bool = False
) -> float:
    """
    Calcula o Imposto de Renda sobre o lucro de um ativo.
    
    Args:
        tipo_ativo: 'cdb', 'lci', 'lca', 'acao', 'cripto', 'fundo', etc.
        data_compra: Data da compra
        data_venda: Data da venda
        lucro: Lucro obtido na operação (valor_venda - valor_compra)
        valor_vendido_mes: Valor total vendido no mês (para cripto)
        is_day_trade: Se é day trade (para ações)
    
    Returns:
        Valor do IR a pagar
    """
    if lucro <= 0:
        return 0.0
    
    # Ativos isentos (LCI, LCA, CRI, CRA, etc.)
    if is_ativo_isento(tipo_ativo):
        return 0.0
    
    # Criptomoedas
    if tipo_ativo == "cripto":
        aliquota = get_aliquota_cripto(valor_vendido_mes)
        return lucro * aliquota
    
    # Ações
    if tipo_ativo == "acao":
        aliquota = get_aliquota_acao(day_trade=is_day_trade)
        return lucro * aliquota
    
    # Fundos de investimento
    if tipo_ativo == "fundo":
        aliquota = get_aliquota_fundo_investimento()
        return lucro * aliquota
    
    # Renda Fixa (CDB, Tesouro, Debêntures, etc.)
    prazo = (data_venda - data_compra).days
    aliquota = get_aliquota_ir_renda_fixa(prazo)
    
    return lucro * aliquota


def calcular_ir_venda_parcial(
    tipo_ativo: str,
    data_compra: date,
    data_venda: date,
    quantidade_vendida: float,
    preco_medio_compra: float,
    preco_venda: float,
    valor_vendido_mes: float = 0
) -> float:
    """
    Calcula o IR para venda parcial de uma posição.
    """
    lucro = quantidade_vendida * (preco_venda - preco_medio_compra)
    
    return calcular_ir(
        tipo_ativo=tipo_ativo,
        data_compra=data_compra,
        data_venda=data_venda,
        lucro=lucro,
        valor_vendido_mes=valor_vendido_mes
    )
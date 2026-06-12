# services/renda_fixa_engine.py

from datetime import date
from typing import Dict, Optional
from services.market.historical_service import buscar_taxas_cdi_periodo, buscar_taxas_ipca_periodo


def calcular_renda_fixa(
    tipo_ativo: str,          # 'cdb', 'lci', 'lca', 'tesouro'
    indexador: str,           # 'CDI', 'IPCA', 'PRE'
    valor_inicial: float,
    data_compra: date,
    data_final: date,
    taxa_contratada: float    # 110 -> 110% do CDI; 6.5 -> IPCA+6,5% a.a.; 12.5 -> prefixado 12,5% a.a.
) -> Dict[str, float]:
    """
    Calcula o valor bruto, rendimento, imposto e valor líquido de um ativo de renda fixa.
    """
    if valor_inicial <= 0 or data_compra >= data_final:
        return {
            "valor_bruto": valor_inicial,
            "rendimento_bruto": 0.0,
            "imposto": 0.0,
            "valor_liquido": valor_inicial,
            "aliquota": 0.0,
        }

    # 1. Cálculo do valor bruto conforme o indexador
    if indexador == "CDI":
        valor_bruto = _calcular_cdi(valor_inicial, data_compra, data_final, taxa_contratada)
    elif indexador == "IPCA":
        valor_bruto = _calcular_ipca(valor_inicial, data_compra, data_final, taxa_contratada)
    else:  # PRE (prefixado)
        valor_bruto = _calcular_prefixado(valor_inicial, data_compra, data_final, taxa_contratada)

    rendimento_bruto = valor_bruto - valor_inicial
    dias = (data_final - data_compra).days

    # 2. Cálculo do Imposto de Renda
    if _is_isento(tipo_ativo):
        aliquota = 0.0
    else:
        aliquota = _get_aliquota_ir(dias)

    imposto = rendimento_bruto * aliquota
    valor_liquido = valor_bruto - imposto

    return {
        "valor_bruto": round(valor_bruto, 2),
        "rendimento_bruto": round(rendimento_bruto, 2),
        "imposto": round(imposto, 2),
        "valor_liquido": round(valor_liquido, 2),
        "aliquota": round(aliquota * 100, 2),
    }


def _calcular_cdi(valor: float, inicio: date, fim: date, percentual_cdi: float) -> float:
    """
    CDI pós‑fixado: usa as taxas mensais históricas do CDI.
    Para cada mês, aplica (1 + taxa_mensal * (percentual_cdi/100)).
    """
    fator = 1.0
    taxas_mensais = buscar_taxas_cdi_periodo(inicio, fim)  # dict { 'YYYY-MM': taxa_mensal }
    ano = inicio.year
    mes = inicio.month
    while date(ano, mes, 1) <= fim:
        chave = f"{ano}-{mes:02d}"
        cdi_mes = taxas_mensais.get(chave, 0.0085)  # fallback 0,85% ao mês
        rentabilidade_mes = cdi_mes * (percentual_cdi / 100.0)
        fator *= (1 + rentabilidade_mes)
        if mes == 12:
            mes = 1
            ano += 1
        else:
            mes += 1
    return valor * fator


def _calcular_ipca(valor: float, inicio: date, fim: date, taxa_extra_anual: float) -> float:
    """
    IPCA + taxa fixa anual:
    - Acumula a inflação real mês a mês (IPCA).
    - Adiciona o componente fixo anual: (1 + taxa_extra/100) ^ (dias/365).
    """
    fator_ipca = 1.0
    taxas_ipca_mensais = buscar_taxas_ipca_periodo(inicio, fim)
    ano = inicio.year
    mes = inicio.month
    while date(ano, mes, 1) <= fim:
        chave = f"{ano}-{mes:02d}"
        ipca_mes = taxas_ipca_mensais.get(chave, 0.004)  # fallback 0,4%
        fator_ipca *= (1 + ipca_mes)
        if mes == 12:
            mes = 1
            ano += 1
        else:
            mes += 1
    dias = (fim - inicio).days
    fator_fixo = (1 + taxa_extra_anual / 100.0) ** (dias / 365.0)
    return valor * fator_ipca * fator_fixo


def _calcular_prefixado(valor: float, inicio: date, fim: date, taxa_anual: float) -> float:
    """
    Prefixado: juros compostos com base anual, contagem de dias corridos (365).
    """
    dias = (fim - inicio).days
    fator = (1 + taxa_anual / 100.0) ** (dias / 365.0)
    return valor * fator


def _is_isento(tipo_ativo: str) -> bool:
    """Verifica se o ativo é isento de Imposto de Renda."""
    isentos = ["lci", "lca", "cri", "cra"]
    return tipo_ativo.lower() in isentos


def _get_aliquota_ir(dias: int) -> float:
    """Retorna a alíquota de IR com base na tabela regressiva."""
    if dias <= 180:
        return 0.225
    elif dias <= 360:
        return 0.20
    elif dias <= 720:
        return 0.175
    else:
        return 0.15
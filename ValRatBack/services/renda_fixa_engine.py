# services/renda_fixa_engine.py

from datetime import date
from typing import Dict, Optional
from services.market.indicadores_service import buscar_cdi_periodo, buscar_ipca_periodo


def calcular_renda_fixa(
    tipo_ativo: str,          # 'cdb', 'lci', 'lca', 'tesouro'
    indexador: str,           # 'CDI', 'IPCA', 'PRE'
    valor_inicial: float,
    data_compra: date,
    data_final: date,
    taxa_contratada: float    
) -> Dict[str, float]:

    if valor_inicial <= 0 or data_compra >= data_final:
        return {
            "valor_bruto": valor_inicial,
            "rendimento_bruto": 0.0,
            "imposto": 0.0,
            "valor_liquido": valor_inicial,
            "aliquota": 0.0,
        }

    if indexador == "CDI":
        valor_bruto = _calcular_cdi(valor_inicial, data_compra, data_final, taxa_contratada)
    elif indexador == "IPCA":
        valor_bruto = _calcular_ipca(valor_inicial, data_compra, data_final, taxa_contratada)
    else:
        valor_bruto = _calcular_prefixado(valor_inicial, data_compra, data_final, taxa_contratada)

    rendimento_bruto = valor_bruto - valor_inicial
    dias = (data_final - data_compra).days

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

    fator = 1.0
    taxas_mensais = buscar_cdi_periodo(inicio, fim)
    ano = inicio.year
    mes = inicio.month
    while date(ano, mes, 1) <= fim:
        chave = f"{ano}-{mes:02d}"
        cdi_mes = taxas_mensais.get(chave, 0.0085)
        rentabilidade_mes = cdi_mes * (percentual_cdi / 100.0)
        fator *= (1 + rentabilidade_mes)
        if mes == 12:
            mes = 1
            ano += 1
        else:
            mes += 1
    return valor * fator


def _calcular_ipca(valor: float, inicio: date, fim: date, taxa_extra_anual: float) -> float:

    fator_ipca = 1.0
    taxas_ipca_mensais = buscar_ipca_periodo(inicio, fim)
    ano = inicio.year
    mes = inicio.month
    while date(ano, mes, 1) <= fim:
        chave = f"{ano}-{mes:02d}"
        ipca_mes = taxas_ipca_mensais.get(chave, 0.004)
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

    dias = (fim - inicio).days
    fator = (1 + taxa_anual / 100.0) ** (dias / 365.0)
    return valor * fator


def _is_isento(tipo_ativo: str) -> bool:
    isentos = ["lci", "lca", "cri", "cra"]
    return tipo_ativo.lower() in isentos


def _get_aliquota_ir(dias: int) -> float:
    if dias <= 180:
        return 0.225
    elif dias <= 360:
        return 0.20
    elif dias <= 720:
        return 0.175
    else:
        return 0.15
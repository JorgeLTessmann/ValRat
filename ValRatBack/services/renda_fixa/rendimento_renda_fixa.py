from typing import Sequence, List
from dataclasses import dataclass

from .estrategias_indexador import EstrategiaIndexador

DIAS_UTEIS_ANO_PADRAO_MERCADO = 252

@dataclass
class ParametrosInvestimentoRendaFixa:
    valor_presente: float
    percentual_indexador_contratado: float
    taxas_anuais_indexador_por_dia_util: Sequence[float]
    dias_uteis_por_ano: int = DIAS_UTEIS_ANO_PADRAO_MERCADO

def converter_taxa_anual_para_taxa_diaria(
    taxa_anual_decimal: float,
    dias_uteis_por_ano: int = DIAS_UTEIS_ANO_PADRAO_MERCADO,
) -> float:
    return (1.0 + taxa_anual_decimal) ** (1.0 / dias_uteis_por_ano) - 1.0

def calcular_fator_diario_capitalizacao(
    taxa_anual_indexador_decimal: float,
    percentual_indexador_contratado: float,
    dias_uteis_por_ano: int = DIAS_UTEIS_ANO_PADRAO_MERCADO,
) -> float:
    taxa_diaria_equivalente = converter_taxa_anual_para_taxa_diaria(
        taxa_anual_indexador_decimal, dias_uteis_por_ano
    )
    taxa_diaria_contratada = taxa_diaria_equivalente * percentual_indexador_contratado
    return 1.0 + taxa_diaria_contratada

def calcular_valor_futuro_renda_fixa(
    parametros: ParametrosInvestimentoRendaFixa,
) -> float:
    fator_produtorio_acumulado = 1.0

    for taxa_anual_do_dia in parametros.taxas_anuais_indexador_por_dia_util:
        fator_do_dia = calcular_fator_diario_capitalizacao(
            taxa_anual_indexador_decimal=taxa_anual_do_dia,
            percentual_indexador_contratado=parametros.percentual_indexador_contratado,
            dias_uteis_por_ano=parametros.dias_uteis_por_ano,
        )
        fator_produtorio_acumulado *= fator_do_dia

    valor_futuro = parametros.valor_presente * fator_produtorio_acumulado
    return valor_futuro

def calcular_valor_futuro_por_estrategia(
    valor_presente: float,
    estrategia: EstrategiaIndexador,
) -> float:
    fator_produtorio_acumulado = 1.0

    for indice_dia_util in range(estrategia.quantidade_dias_uteis()):
        fator_do_dia = estrategia.calcular_fator_diario(indice_dia_util)
        fator_produtorio_acumulado *= fator_do_dia

    valor_futuro = valor_presente * fator_produtorio_acumulado
    return valor_futuro

def gerar_serie_taxa_constante(
    taxa_anual_decimal: float,
    quantidade_dias_uteis: int,
) -> List[float]:
    return [taxa_anual_decimal] * quantidade_dias_uteis

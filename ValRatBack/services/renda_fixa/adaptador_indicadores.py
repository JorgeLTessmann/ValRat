from datetime import date, timedelta
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, field

import numpy as np

from .rendimento_renda_fixa import (
    DIAS_UTEIS_ANO_PADRAO_MERCADO,
    ParametrosInvestimentoRendaFixa,
    calcular_valor_futuro_renda_fixa,
    calcular_valor_futuro_por_estrategia,
)
from .estrategias_indexador import (
    PosFixadoPercentualIndexador,
    PreFixado,
    IPCAMaisSpread,
)

def contar_dias_uteis_no_mes(
    ano: int,
    mes: int,
    feriados: Optional[List[date]] = None,
) -> int:
    primeiro_dia_mes = date(ano, mes, 1)
    primeiro_dia_mes_seguinte = (
        date(ano + 1, 1, 1) if mes == 12 else date(ano, mes + 1, 1)
    )

    feriados_no_periodo = feriados if feriados else []

    quantidade_dias_uteis = np.busday_count(
        primeiro_dia_mes.isoformat(),
        primeiro_dia_mes_seguinte.isoformat(),
        holidays=[f.isoformat() for f in feriados_no_periodo],
    )
    return int(quantidade_dias_uteis)

def listar_dias_uteis_no_mes(
    ano: int,
    mes: int,
    feriados: Optional[List[date]] = None,
) -> List[date]:
    primeiro_dia_mes = date(ano, mes, 1)
    primeiro_dia_mes_seguinte = (
        date(ano + 1, 1, 1) if mes == 12 else date(ano, mes + 1, 1)
    )

    feriados_no_periodo = feriados if feriados else []

    array_dias_uteis = np.arange(
        primeiro_dia_mes.isoformat(),
        primeiro_dia_mes_seguinte.isoformat(),
        dtype="datetime64[D]",
    )
    mascara_dias_uteis = np.is_busday(
        array_dias_uteis,
        holidays=[f.isoformat() for f in feriados_no_periodo],
    )
    dias_uteis_filtrados = array_dias_uteis[mascara_dias_uteis]

    return [d.item() for d in dias_uteis_filtrados]

def converter_taxa_mensal_acumulada_para_taxa_anual_equivalente(
    taxa_mensal_acumulada_decimal: float,
    quantidade_dias_uteis_do_mes: int,
    dias_uteis_por_ano: int = DIAS_UTEIS_ANO_PADRAO_MERCADO,
) -> float:
    if quantidade_dias_uteis_do_mes <= 0:
        raise ValueError(
            "quantidade_dias_uteis_do_mes deve ser maior que zero "
            f"(recebido: {quantidade_dias_uteis_do_mes})"
        )

    taxa_diaria_equivalente = (
        (1.0 + taxa_mensal_acumulada_decimal) ** (1.0 / quantidade_dias_uteis_do_mes)
        - 1.0
    )
    taxa_anual_equivalente = (
        (1.0 + taxa_diaria_equivalente) ** dias_uteis_por_ano - 1.0
    )
    return taxa_anual_equivalente

@dataclass
class FonteDadosIndicador:
    buscar_taxa_mensal: Callable[[int, int], Optional[float]]
    taxa_mensal_fallback: float = 0.0085

def montar_serie_diaria_taxa_anual_equivalente(
    data_inicio: date,
    data_fim: date,
    fonte_dados: FonteDadosIndicador,
    feriados: Optional[List[date]] = None,
    dias_uteis_por_ano: int = DIAS_UTEIS_ANO_PADRAO_MERCADO,
) -> List[float]:
    if data_fim < data_inicio:
        raise ValueError(
            f"data_fim ({data_fim}) não pode ser anterior a data_inicio ({data_inicio})"
        )

    serie_diaria_taxa_anual_equivalente: List[float] = []

    ano_corrente = data_inicio.year
    mes_corrente = data_inicio.month

    while date(ano_corrente, mes_corrente, 1) <= data_fim:
        dias_uteis_do_mes = listar_dias_uteis_no_mes(
            ano_corrente, mes_corrente, feriados=feriados
        )

        dias_uteis_do_mes_no_periodo = [
            d for d in dias_uteis_do_mes if data_inicio <= d <= data_fim
        ]

        if dias_uteis_do_mes_no_periodo:
            taxa_mensal = fonte_dados.buscar_taxa_mensal(ano_corrente, mes_corrente)
            if taxa_mensal is None:
                taxa_mensal = fonte_dados.taxa_mensal_fallback

            taxa_anual_equivalente = converter_taxa_mensal_acumulada_para_taxa_anual_equivalente(
                taxa_mensal_acumulada_decimal=taxa_mensal,
                quantidade_dias_uteis_do_mes=len(dias_uteis_do_mes),
                dias_uteis_por_ano=dias_uteis_por_ano,
            )

            serie_diaria_taxa_anual_equivalente.extend(
                [taxa_anual_equivalente] * len(dias_uteis_do_mes_no_periodo)
            )

        if mes_corrente == 12:
            mes_corrente = 1
            ano_corrente += 1
        else:
            mes_corrente += 1

    return serie_diaria_taxa_anual_equivalente

def calcular_valor_futuro_a_partir_de_taxas_mensais(
    valor_presente: float,
    percentual_indexador_contratado: float,
    data_inicio: date,
    data_fim: date,
    fonte_dados: FonteDadosIndicador,
    feriados: Optional[List[date]] = None,
    dias_uteis_por_ano: int = DIAS_UTEIS_ANO_PADRAO_MERCADO,
) -> float:
    serie_diaria_taxa_anual_equivalente = montar_serie_diaria_taxa_anual_equivalente(
        data_inicio=data_inicio,
        data_fim=data_fim,
        fonte_dados=fonte_dados,
        feriados=feriados,
        dias_uteis_por_ano=dias_uteis_por_ano,
    )

    parametros = ParametrosInvestimentoRendaFixa(
        valor_presente=valor_presente,
        percentual_indexador_contratado=percentual_indexador_contratado,
        taxas_anuais_indexador_por_dia_util=serie_diaria_taxa_anual_equivalente,
        dias_uteis_por_ano=dias_uteis_por_ano,
    )

    return calcular_valor_futuro_renda_fixa(parametros)

def calcular_valor_futuro_prefixado(
    valor_presente: float,
    taxa_anual_prefixada: float,
    data_inicio: date,
    data_fim: date,
    feriados: Optional[List[date]] = None,
    dias_uteis_por_ano: int = DIAS_UTEIS_ANO_PADRAO_MERCADO,
) -> float:
    if data_fim < data_inicio:
        raise ValueError(
            f"data_fim ({data_fim}) não pode ser anterior a data_inicio ({data_inicio})"
        )

    feriados_no_periodo = feriados if feriados else []
    quantidade_dias_uteis_periodo = int(
        np.busday_count(
            data_inicio.isoformat(),
            (data_fim + timedelta(days=1)).isoformat(),
            holidays=[f.isoformat() for f in feriados_no_periodo],
        )
    )

    estrategia = PreFixado(
        taxa_anual_prefixada=taxa_anual_prefixada,
        quantidade_total_dias_uteis=quantidade_dias_uteis_periodo,
        dias_uteis_por_ano=dias_uteis_por_ano,
    )

    return calcular_valor_futuro_por_estrategia(
        valor_presente=valor_presente,
        estrategia=estrategia,
    )

def calcular_valor_futuro_ipca_mais_spread(
    valor_presente: float,
    taxa_real_anual_prefixada: float,
    data_inicio: date,
    data_fim: date,
    fonte_dados_ipca: FonteDadosIndicador,
    feriados: Optional[List[date]] = None,
    dias_uteis_por_ano: int = DIAS_UTEIS_ANO_PADRAO_MERCADO,
) -> float:
    serie_diaria_ipca_anual_equivalente = montar_serie_diaria_taxa_anual_equivalente(
        data_inicio=data_inicio,
        data_fim=data_fim,
        fonte_dados=fonte_dados_ipca,
        feriados=feriados,
        dias_uteis_por_ano=dias_uteis_por_ano,
    )

    estrategia = IPCAMaisSpread(
        taxas_anuais_ipca_por_dia_util=serie_diaria_ipca_anual_equivalente,
        taxa_real_anual_prefixada=taxa_real_anual_prefixada,
        dias_uteis_por_ano=dias_uteis_por_ano,
    )

    return calcular_valor_futuro_por_estrategia(
        valor_presente=valor_presente,
        estrategia=estrategia,
    )

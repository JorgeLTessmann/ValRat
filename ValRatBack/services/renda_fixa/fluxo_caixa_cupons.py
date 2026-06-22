from __future__ import annotations

import warnings
from dataclasses import dataclass
from datetime import date, timedelta
from typing import List, Optional, Set

from dateutil.relativedelta import relativedelta

try:
    import holidays as _holidays_lib
    _BIBLIOTECA_HOLIDAYS_DISPONIVEL = True
except ImportError:
    _BIBLIOTECA_HOLIDAYS_DISPONIVEL = False

MESES_POR_SEMESTRE = 6

FERIADOS_NACIONAIS_FIXOS_MES_DIA = {
    (1, 1):   "Confraternização Universal",
    (4, 21):  "Tiradentes",
    (5, 1):   "Dia do Trabalhador",
    (9, 7):   "Independência do Brasil",
    (10, 12): "Nossa Senhora Aparecida",
    (11, 2):  "Finados",
    (11, 15): "Proclamação da República",
    (12, 25): "Natal",
}

def obter_feriados_nacionais(anos: List[int]) -> Set[date]:
    if _BIBLIOTECA_HOLIDAYS_DISPONIVEL:
        feriados_brasil = _holidays_lib.Brazil(years=anos)  
        return set(feriados_brasil.keys())

    warnings.warn(
        "Biblioteca 'holidays' não está instalada — usando apenas feriados "
        "nacionais de data fixa. Para ajuste mais preciso: pip install holidays",
        stacklevel=2,
    )
    feriados: Set[date] = set()
    for ano in anos:
        for (mes, dia), _nome in FERIADOS_NACIONAIS_FIXOS_MES_DIA.items():
            feriados.add(date(ano, mes, dia))
    return feriados

def ajustar_para_proximo_dia_util(
    data_referencia: date,
    feriados: Set[date],
) -> date:
    data_ajustada = data_referencia
    while data_ajustada.weekday() >= 5 or data_ajustada in feriados:
        data_ajustada += timedelta(days=1)
    return data_ajustada

@dataclass(frozen=True)
class PagamentoFluxoCaixa:
    data_pagamento_prevista: date
    data_pagamento_efetiva: date
    valor_cupom: float
    valor_principal: float
    numero_pagamento: int
    eh_pagamento_pro_rata: bool

    @property
    def valor_total(self) -> float:
        return self.valor_cupom + self.valor_principal

@dataclass(frozen=True)
class FluxoCaixaTituloComCupom:
    valor_presente_investido: float
    taxa_anual_prefixada: float
    data_compra: date
    data_vencimento: date
    pagamentos: List[PagamentoFluxoCaixa]

    @property
    def valor_total_recebido(self) -> float:
        return sum(pagamento.valor_total for pagamento in self.pagamentos)

    @property
    def total_juros_recebidos(self) -> float:
        return sum(pagamento.valor_cupom for pagamento in self.pagamentos)

def calcular_valor_cupom_semestral_cheio(
    valor_presente: float,
    taxa_anual_prefixada: float,
) -> float:
    taxa_semestral_equivalente = (1.0 + taxa_anual_prefixada) ** 0.5 - 1.0
    return valor_presente * taxa_semestral_equivalente

def gerar_datas_base_cupom(
    data_compra: date,
    data_vencimento: date,
) -> List[date]:
    if data_vencimento <= data_compra:
        raise ValueError(
            f"data_vencimento ({data_vencimento}) deve ser posterior a "
            f"data_compra ({data_compra})"
        )
    if (data_vencimento.month, data_vencimento.day) != (1, 1):
        raise ValueError(
            f"data_vencimento ({data_vencimento}) deve cair em 1º de "
            "janeiro, conforme a convenção de vencimento da NTN-F."
        )

    datas_base_em_ordem_reversa: List[date] = [data_vencimento]
    data_corrente = data_vencimento

    while True:
        data_corrente = data_corrente - relativedelta(months=MESES_POR_SEMESTRE)
        datas_base_em_ordem_reversa.append(data_corrente)
        if data_corrente <= data_compra:
            break

    return list(reversed(datas_base_em_ordem_reversa))

def calcular_fluxo_caixa_titulo_com_cupom_semestral(
    valor_presente: float,
    taxa_anual_prefixada: float,
    data_compra: date,
    data_vencimento: date,
    feriados: Optional[Set[date]] = None,
) -> FluxoCaixaTituloComCupom:
    datas_base = gerar_datas_base_cupom(data_compra, data_vencimento)
    data_base_anterior_a_compra = datas_base[0]
    datas_de_pagamento = datas_base[1:]

    if feriados is None:
        anos_cobertos = list(range(data_compra.year, data_vencimento.year + 1))
        feriados = obter_feriados_nacionais(anos_cobertos)

    cupom_cheio = calcular_valor_cupom_semestral_cheio(valor_presente, taxa_anual_prefixada)

    pagamentos: List[PagamentoFluxoCaixa] = []
    ultimo_indice = len(datas_de_pagamento)

    for indice, data_base_pagamento in enumerate(datas_de_pagamento, start=1):
        eh_primeiro_pagamento = indice == 1
        eh_pagamento_final = indice == ultimo_indice

        if eh_primeiro_pagamento:
            dias_totais_do_semestre = (data_base_pagamento - data_base_anterior_a_compra).days
            dias_efetivamente_possuidos = (data_base_pagamento - data_compra).days
            fracao_possuida = dias_efetivamente_possuidos / dias_totais_do_semestre
            valor_cupom_deste_pagamento = cupom_cheio * fracao_possuida
            eh_pro_rata = fracao_possuida < 1.0
        else:
            valor_cupom_deste_pagamento = cupom_cheio
            eh_pro_rata = False

        data_efetiva = ajustar_para_proximo_dia_util(data_base_pagamento, feriados)

        pagamentos.append(
            PagamentoFluxoCaixa(
                data_pagamento_prevista=data_base_pagamento,
                data_pagamento_efetiva=data_efetiva,
                valor_cupom=valor_cupom_deste_pagamento,
                valor_principal=valor_presente if eh_pagamento_final else 0.0,
                numero_pagamento=indice,
                eh_pagamento_pro_rata=eh_pro_rata,
            )
        )

    return FluxoCaixaTituloComCupom(
        valor_presente_investido=valor_presente,
        taxa_anual_prefixada=taxa_anual_prefixada,
        data_compra=data_compra,
        data_vencimento=data_vencimento,
        pagamentos=pagamentos,
    )

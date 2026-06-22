from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Sequence

DIAS_UTEIS_ANO_PADRAO_MERCADO = 252

class EstrategiaIndexador(ABC):
    @abstractmethod
    def calcular_fator_diario(self, indice_dia_util: int) -> float:
        raise NotImplementedError

    @abstractmethod
    def quantidade_dias_uteis(self) -> int:
        raise NotImplementedError

@dataclass
class PosFixadoPercentualIndexador(EstrategiaIndexador):
    taxas_anuais_indexador_por_dia_util: Sequence[float]
    percentual_indexador_contratado: float
    dias_uteis_por_ano: int = DIAS_UTEIS_ANO_PADRAO_MERCADO

    def calcular_fator_diario(self, indice_dia_util: int) -> float:
        taxa_anual_do_dia = self.taxas_anuais_indexador_por_dia_util[indice_dia_util]
        taxa_diaria_equivalente = (
            (1.0 + taxa_anual_do_dia) ** (1.0 / self.dias_uteis_por_ano) - 1.0
        )
        taxa_diaria_contratada = taxa_diaria_equivalente * self.percentual_indexador_contratado
        return 1.0 + taxa_diaria_contratada

    def quantidade_dias_uteis(self) -> int:
        return len(self.taxas_anuais_indexador_por_dia_util)

@dataclass
class PreFixado(EstrategiaIndexador):
    taxa_anual_prefixada: float
    quantidade_total_dias_uteis: int
    dias_uteis_por_ano: int = DIAS_UTEIS_ANO_PADRAO_MERCADO

    def calcular_fator_diario(self, indice_dia_util: int) -> float:
        taxa_diaria_equivalente = (
            (1.0 + self.taxa_anual_prefixada) ** (1.0 / self.dias_uteis_por_ano) - 1.0
        )
        return 1.0 + taxa_diaria_equivalente

    def quantidade_dias_uteis(self) -> int:
        return self.quantidade_total_dias_uteis

@dataclass
class IPCAMaisSpread(EstrategiaIndexador):
    taxas_anuais_ipca_por_dia_util: Sequence[float]
    taxa_real_anual_prefixada: float
    dias_uteis_por_ano: int = DIAS_UTEIS_ANO_PADRAO_MERCADO

    def calcular_fator_diario(self, indice_dia_util: int) -> float:
        taxa_anual_ipca_do_dia = self.taxas_anuais_ipca_por_dia_util[indice_dia_util]

        ipca_diario_equivalente = (
            (1.0 + taxa_anual_ipca_do_dia) ** (1.0 / self.dias_uteis_por_ano) - 1.0
        )
        spread_diario_equivalente = (
            (1.0 + self.taxa_real_anual_prefixada) ** (1.0 / self.dias_uteis_por_ano) - 1.0
        )

        fator_diario_combinado = (1.0 + ipca_diario_equivalente) * (1.0 + spread_diario_equivalente)
        return fator_diario_combinado

    def quantidade_dias_uteis(self) -> int:
        return len(self.taxas_anuais_ipca_por_dia_util)

# services/renda_fixa/calculadora_renda_fixa.py

from datetime import datetime, date
from typing import Optional
from constants.asset_types import CDI, SELIC, IPCA, PRE

# Taxas padrão para fallback (caso APIs estejam offline)
TAXAS_PADRAO = {
    CDI: 0.105,    # 10.5% ao ano
    SELIC: 0.105,  # 10.5% ao ano
    IPCA: 0.045    # 4.5% ao ano
}

def buscar_taxa_indexador_seguro(indexador: str) -> float:
    """
    Busca taxa do indexador com fallback seguro.
    Prioriza API, mas usa valores padrão se falhar.
    """
    from services.renda_fixa.indexadores_service import buscar_taxa_indexador
    
    taxa = buscar_taxa_indexador(indexador)
    
    if taxa is None and indexador in TAXAS_PADRAO:
        print(f"⚠️ Usando taxa padrão para {indexador}: {TAXAS_PADRAO[indexador]}")
        return TAXAS_PADRAO[indexador]
    
    return taxa or 0.0


def converter_para_date(data) -> date:
    """Converte string, datetime ou date para date"""
    if isinstance(data, date):
        return data
    if isinstance(data, datetime):
        return data.date()
    if isinstance(data, str):
        # Remove timezone se existir
        if "T" in data:
            data = data.split("T")[0]
        if " " in data:
            data = data.split(" ")[0]
        # Tenta formatos comuns
        for fmt in ["%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d"]:
            try:
                return datetime.strptime(data, fmt).date()
            except ValueError:
                continue
    raise ValueError(f"Formato de data não suportado: {data}")


def calcular_valor_renda_fixa(
    valor_inicial: float,
    taxa: float,
    indexador: str,
    data_compra,
    data_final=None
) -> float:
    """
    Calcula o valor atual de um ativo de renda fixa.
    """
    if valor_inicial <= 0:
        return 0.0
    
    # Converte datas
    data_compra = converter_para_date(data_compra)
    
    if data_final is None:
        data_final = date.today()
    else:
        data_final = converter_para_date(data_final)
    
    # Se a data de compra é futura, retorna o valor inicial
    if data_compra > data_final:
        return valor_inicial
    
    # Calcula dias e anos corridos
    dias = (data_final - data_compra).days
    anos = max(dias / 365, 0)  # Não permite negativo
    
    if anos == 0:
        return valor_inicial
    
    # =========================
    # PREFIXADO
    # =========================
    if indexador == PRE:
        taxa_anual = taxa / 100
    
    # =========================
    # INDEXADO (CDI, SELIC, IPCA)
    # =========================
    else:
        taxa_base = buscar_taxa_indexador_seguro(indexador)
        # taxa vem em percentual (ex: 110 = 110%)
        # taxa_base é decimal (ex: 0.105 = 10.5%)
        taxa_anual = taxa_base * (taxa / 100)
    
    # Juros compostos
    valor_bruto = valor_inicial * ((1 + taxa_anual) ** anos)
    
    return round(valor_bruto, 2)
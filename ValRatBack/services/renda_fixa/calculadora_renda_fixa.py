# services/renda_fixa/calculadora_renda_fixa.py

from datetime import date, datetime
from services.market.historical_service import buscar_taxas_cdi_periodo, buscar_taxas_ipca_periodo
from services.market.indicadores_service import buscar_cdi_periodo, buscar_ipca_periodo


def converter_data(valor):
    if isinstance(valor, date):
        return valor
    if isinstance(valor, datetime):
        return valor.date()
    if isinstance(valor, str):
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d"):
            try:
                return datetime.strptime(valor, fmt).date()
            except:
                continue
    raise ValueError(f"Data inválida: {valor}")

def calcular_valor_renda_fixa(
    valor_inicial: float,
    taxa: float,          # percentual do CDB (ex: 110)
    indexador: str,
    data_compra,
    data_final=None
) -> float:
    if valor_inicial <= 0:
        return 0.0

    data_compra = converter_data(data_compra)
    if data_final is None:
        data_final = date.today()
    else:
        data_final = converter_data(data_final)

    if data_compra >= data_final:
        return valor_inicial

    # ----- PREFIXADO (taxa fixa) -----
    if indexador.upper() == "PRE":
        taxa_anual = taxa / 100.0
        dias = (data_final - data_compra).days
        taxa_diaria = (1 + taxa_anual) ** (1/365) - 1
        valor_final = valor_inicial * (1 + taxa_diaria) ** dias
        return round(valor_final, 2)

    # ----- INDEXADOS (CDI ou IPCA) -----
    if indexador.upper() == "CDI":
        taxas_mensais = buscar_taxas_cdi_periodo(data_compra, data_final)
        fator = 1.0
        ano = data_compra.year
        mes = data_compra.month
        while date(ano, mes, 1) <= data_final:
            chave = f"{ano}-{mes:02d}"
            cdi_mes = taxas_mensais.get(chave, 0.0085)
            rentabilidade_mes = cdi_mes * (taxa / 100.0)
            fator *= (1 + rentabilidade_mes)
            if mes == 12:
                mes = 1
                ano += 1
            else:
                mes += 1
        return round(valor_inicial * fator, 2)

    if indexador.upper() == "IPCA":
        taxas_mensais = buscar_taxas_ipca_periodo(data_compra, data_final)
        fator = 1.0
        ano = data_compra.year
        mes = data_compra.month
        while date(ano, mes, 1) <= data_final:
            chave = f"{ano}-{mes:02d}"
            ipca_mes = taxas_mensais.get(chave, 0.004)
            rentabilidade_mes = ipca_mes * (taxa / 100.0) if taxa != 0 else ipca_mes
            fator *= (1 + rentabilidade_mes)
            if mes == 12:
                mes = 1
                ano += 1
            else:
                mes += 1
        return round(valor_inicial * fator, 2)

    return valor_inicial
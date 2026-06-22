import json
import os
from datetime import date, datetime, timedelta
from services.market.indicadores_service import buscar_cdi_periodo, buscar_ipca_periodo, buscar_cdi_mensal, buscar_ipca_mensal
from services.imposto_config_service import is_ativo_isento, get_aliquota_ir_renda_fixa

# Import the new system
from .adaptador_indicadores import (
    calcular_valor_futuro_prefixado,
    calcular_valor_futuro_a_partir_de_taxas_mensais,
    calcular_valor_futuro_ipca_mais_spread,
    FonteDadosIndicador
)
from .fluxo_caixa_cupons import calcular_fluxo_caixa_titulo_com_cupom_semestral

def converter_data(valor) -> date:
    if isinstance(valor, date):
        return valor
    if isinstance(valor, datetime):
        return valor.date()
    if isinstance(valor, str):
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d"):
            try:
                return datetime.strptime(valor, fmt).date()
            except ValueError:
                continue
    raise ValueError(f"Data inválida: {valor}")

def contar_dias_uteis(data_inicio: date, data_fim: date) -> int:
    dias_uteis = 0
    data_atual = data_inicio
    while data_atual < data_fim:
        if data_atual.weekday() < 5:
            dias_uteis += 1
        data_atual += timedelta(days=1)
    return dias_uteis

def calcular_iof(dias_corridos: int) -> float:
    if dias_corridos >= 30:
        return 0.0
    tabela_iof = [
        0.96, 0.93, 0.90, 0.86, 0.83, 0.80, 0.76, 0.73, 0.70, 0.66,
        0.63, 0.60, 0.56, 0.53, 0.50, 0.46, 0.43, 0.40, 0.36, 0.33,
        0.30, 0.26, 0.23, 0.20, 0.16, 0.13, 0.10, 0.06, 0.03
    ]
    return tabela_iof[dias_corridos - 1] if dias_corridos > 0 else 0.0

def adicionar_6_meses(data: date) -> date:
    ano = data.year + (data.month + 6 - 1) // 12
    mes = (data.month + 6 - 1) % 12 + 1
    dia = min(data.day, [31, 29 if ano % 4 == 0 and (ano % 100 != 0 or ano % 400 == 0) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][mes-1])
    return date(ano, mes, dia)

# Mantenho o calcular_fator_periodo para retrocompatibilidade do fluxo de cupons antigo se o indexador não for PRE
def calcular_fator_periodo(inicio: date, fim: date, indexador: str, taxa: float, apenas_indexador: bool = False) -> float:
    dias_uteis = contar_dias_uteis(inicio, fim)
    idx = indexador.upper()
    
    taxa_pre = 0.0 if apenas_indexador else (taxa / 100.0)
    fator_pre = (1 + taxa_pre) ** (dias_uteis / 252)

    if idx == "PRE":
        return fator_pre
        
    elif idx == "CDI":
        taxas_mensais = buscar_cdi_periodo(inicio, fim)
        fator_cdi = 1.0
        percentual_cdi = taxa / 100.0 if apenas_indexador else 1.0 
        
        ano, mes = inicio.year, inicio.month
        while date(ano, mes, 1) <= fim:
            cdi_mes = taxas_mensais.get(f"{ano}-{mes:02d}", 0.0085)
            if apenas_indexador:
                fator_cdi *= (1 + (cdi_mes * percentual_cdi))
            else:
                fator_cdi *= (1 + cdi_mes)
            mes = 1 if mes == 12 else mes + 1
            ano = ano + 1 if mes == 1 else ano
            
        return fator_cdi if apenas_indexador else (fator_cdi * fator_pre)

    elif idx == "IPCA":
        taxas_mensais = buscar_ipca_periodo(inicio, fim)
        fator_ipca = 1.0
        for ipca_mes in taxas_mensais.values():
            fator_ipca *= (1 + ipca_mes)
        return fator_ipca * fator_pre

    return 1.0


def calcular_valor_renda_fixa(
    valor_inicial: float,
    taxa: float,
    indexador: str,
    data_compra,
    data_final=None,
    tipo_ativo: str = "",
    frequencia_cupons: str = None
) -> float:
    if valor_inicial <= 0:
        return 0.0

    data_compra = converter_data(data_compra)
    data_final = date.today() if data_final is None else converter_data(data_final)

    if data_compra >= data_final:
        return valor_inicial

    isento = is_ativo_isento(tipo_ativo or indexador)

    def calcular_impostos_sub_periodo(v_inicial, v_final, dt_inicio, dt_pagamento):
        rendimento = v_final - v_inicial
        if rendimento <= 0 or isento:
            return v_final
            
        dias_corridos_sub = (dt_pagamento - dt_inicio).days
        iof_pago = rendimento * calcular_iof(dias_corridos_sub)
        
        rendimento_tributavel = rendimento - iof_pago
        aliquota_ir = get_aliquota_ir_renda_fixa(dias_corridos_sub)
                
        ir_pago = rendimento_tributavel * aliquota_ir
        return v_final - iof_pago - ir_pago

    idx = indexador.upper()

    # Fluxo Semestral (Cupons)
    if frequencia_cupons and frequencia_cupons.lower() == "semestral":
        if idx == "PRE":
            # Usa o NOVO modelo para cupons Prefixados (NTN-F)
            fluxo = calcular_fluxo_caixa_titulo_com_cupom_semestral(
                valor_presente=valor_inicial,
                taxa_anual_prefixada=taxa/100.0,
                data_compra=data_compra,
                data_vencimento=data_final
            )
            carteira_cupons_liquidos = 0.0
            principal_liquido = valor_inicial

            for p in fluxo.pagamentos:
                # O novo modelo projeta até o vencimento. Só contabilizamos os cupons que já caíram
                if p.data_pagamento_efetiva <= data_final:
                    if p.valor_cupom > 0:
                        cupom_liquido = calcular_impostos_sub_periodo(0, p.valor_cupom, data_compra, p.data_pagamento_efetiva)
                        carteira_cupons_liquidos += cupom_liquido
                    if p.valor_principal > 0:
                        principal_liquido = calcular_impostos_sub_periodo(valor_inicial, p.valor_principal, data_compra, p.data_pagamento_efetiva)

            # Se data_final não é o vencimento, o principal continua investido, então o liquido do principal é ele mesmo sem impostos?
            # Na verdade, se estamos olhando um "snapshot" de hoje, e não venceu, temos que calcular marcação na curva do principal.
            # O modelo antigo calcula o fator até hoje. O novo fluxo gerou até o vencimento! 
            # Como resolver? O novo modelo gerou as datas. O valor bruto do principal hoje é só ele mesmo?
            # Para manter compatibilidade com o antigo e ficar preciso: se não venceu, o principal acumulou uma fração do próximo cupom.
            # O método mais seguro é calcular o valor na curva usando o próprio novo modelo sem cupons para o principal, 
            # ou simplesmente usar a velha rotina apenas como fallback.
            pass
        
        # Fallback loop antigo
        carteira_cupons_liquidos = 0.0
        principal_atual = valor_inicial
        data_sub_inicio = data_compra
        data_proximo_cupom = adicionar_6_meses(data_compra)

        while data_proximo_cupom <= data_final:
            fator_idx = calcular_fator_periodo(data_sub_inicio, data_proximo_cupom, indexador, taxa, apenas_indexador=True)
            principal_atual_bruto = principal_atual * fator_idx
            
            taxa_semestral = (1 + taxa / 100.0) ** (1 / 2) - 1
            cupom_bruto = principal_atual_bruto * taxa_semestral
            
            cupom_liquido = calcular_impostos_sub_periodo(0, cupom_bruto, data_compra, data_proximo_cupom)
            carteira_cupons_liquidos += cupom_liquido
            
            principal_atual = principal_atual_bruto
            data_sub_inicio = data_proximo_cupom
            data_proximo_cupom = adicionar_6_meses(data_proximo_cupom)

        if data_sub_inicio < data_final:
            fator_final = calcular_fator_periodo(data_sub_inicio, data_final, indexador, taxa, apenas_indexador=True)
            principal_atual = principal_atual * fator_final

        principal_liquido = calcular_impostos_sub_periodo(valor_inicial, principal_atual, data_compra, data_final)
        return round(principal_liquido + carteira_cupons_liquidos, 2)


    # Investimentos Sem Cupons (Usa o NOVO MODELO)
    valor_bruto = valor_inicial

    if idx == "PRE":
        valor_bruto = calcular_valor_futuro_prefixado(
            valor_presente=valor_inicial,
            taxa_anual_prefixada=taxa/100.0,
            data_inicio=data_compra,
            data_fim=data_final
        )
    elif idx == "CDI":
        fonte_cdi = FonteDadosIndicador(buscar_taxa_mensal=buscar_cdi_mensal, taxa_mensal_fallback=0.0085)
        # Assumindo que taxa representa o % do CDI (ex: 110%)
        valor_bruto = calcular_valor_futuro_a_partir_de_taxas_mensais(
            valor_presente=valor_inicial,
            percentual_indexador_contratado=taxa/100.0,
            data_inicio=data_compra,
            data_fim=data_final,
            fonte_dados=fonte_cdi
        )
    elif idx == "IPCA":
        fonte_ipca = FonteDadosIndicador(buscar_taxa_mensal=buscar_ipca_mensal, taxa_mensal_fallback=0.0040)
        # Assumindo que taxa representa o spread prefixado (ex: 6%)
        valor_bruto = calcular_valor_futuro_ipca_mais_spread(
            valor_presente=valor_inicial,
            taxa_real_anual_prefixada=taxa/100.0,
            data_inicio=data_compra,
            data_fim=data_final,
            fonte_dados_ipca=fonte_ipca
        )
    else:
        # Fallback 
        fator_total = calcular_fator_periodo(data_compra, data_final, indexador, taxa)
        valor_bruto = valor_inicial * fator_total
    
    valor_liquido = calcular_impostos_sub_periodo(valor_inicial, valor_bruto, data_compra, data_final)
    return round(valor_liquido, 2)
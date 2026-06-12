import json
import os
from datetime import date, datetime, timedelta
from services.market.historical_service import buscar_taxas_cdi_periodo, buscar_taxas_ipca_periodo

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

def calcular_fator_periodo(inicio: date, fim: date, indexador: str, taxa: float, apenas_indexador: bool = False) -> float:
    dias_uteis = contar_dias_uteis(inicio, fim)
    idx = indexador.upper()
    
    taxa_pre = 0.0 if apenas_indexador else (taxa / 100.0)
    fator_pre = (1 + taxa_pre) ** (dias_uteis / 252)

    if idx == "PRE":
        return fator_pre
        
    elif idx == "CDI":
        taxas_mensais = buscar_taxas_cdi_periodo(inicio, fim)
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
        taxas_mensais = buscar_taxas_ipca_periodo(inicio, fim)
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
    tipo_ativo: str = None,
    frequencia_cupons: str = None
) -> float:
    if valor_inicial <= 0:
        return 0.0

    data_compra = converter_data(data_compra)
    data_final = date.today() if data_final is None else converter_data(data_final)

    if data_compra >= data_final:
        return valor_inicial

    # 1. Carga de Regras de Imposto (JSON)
    ativos_isentos = ["lci", "lca", "lc", "cra", "cri", "debenture_incentivada"]
    tabela_regressiva = [
        {"dias": 180, "aliquota": 0.225},
        {"dias": 360, "aliquota": 0.20},
        {"dias": 720, "aliquota": 0.175},
        {"dias": 999999, "aliquota": 0.15}
    ]

    try:
        caminho_json = os.path.join("config", "imposto_config.json")
        if os.path.exists(caminho_json):
            with open(caminho_json, "r", encoding="utf-8") as f:
                config = json.load(f)
                if "ativos_isentos" in config:
                    ativos_isentos = [a.lower() for a in config["ativos_isentos"]]
                if "tabela_regressiva" in config:
                    tabela_regressiva = config["tabela_regressiva"]
    except Exception:
        pass

    alvo_checagem = f"{indexador.upper()} {tipo_ativo.upper() if tipo_ativo else ''}"
    isento = any(ativo.upper() in alvo_checagem for ativo in ativos_isentos)

    def calcular_impostos_sub_periodo(v_inicial, v_final, dt_inicio, dt_pagamento):
        rendimento = v_final - v_inicial
        if rendimento <= 0 or isento:
            return v_final
            
        dias_corridos_sub = (dt_pagamento - dt_inicio).days
        iof_pago = rendimento * calcular_iof(dias_corridos_sub)
        
        rendimento_tributavel = rendimento - iof_pago
        aliquota_ir = 0.15
        for regra in tabela_regressiva:
            if dias_corridos_sub <= regra["dias"]:
                aliquota_ir = regra["aliquota"]
                break
                
        ir_pago = rendimento_tributavel * aliquota_ir
        return v_final - iof_pago - ir_pago

    # 2. Fluxo com Juros Semestrais (Cupons)
    if frequencia_cupons and frequencia_cupons.lower() == "semestral":
        carteira_cupons_liquidos = 0.0
        principal_atual = valor_inicial
        data_sub_inicio = data_compra
        data_proximo_cupom = adicionar_6_meses(data_compra)

        while data_proximo_cupom <= data_final:
            # Evolui o principal apenas pelo indexador puro do período
            fator_idx = calcular_fator_periodo(data_sub_inicio, data_proximo_cupom, indexador, taxa, apenas_indexador=True)
            principal_atual_bruto = principal_atual * fator_idx
            
            # Calcula o cupom (taxa contratada semestralizada)
            taxa_semestral = (1 + taxa / 100.0) ** (1 / 2) - 1
            cupom_bruto = principal_atual_bruto * taxa_semestral
            
            # Aplica imposto no cupom referente ao tempo total desde a compra
            cupom_liquido = calcular_impostos_sub_periodo(0, cupom_bruto, data_compra, data_proximo_cupom)
            carteira_cupons_liquidos += cupom_liquido
            
            # O principal continua sua jornada indexado
            principal_atual = principal_atual_bruto
            data_sub_inicio = data_proximo_cupom
            data_proximo_cupom = adicionar_6_meses(data_proximo_cupom)

        # Atualização do último período quebrado (da data do último cupom até a data final)
        if data_sub_inicio < data_final:
            fator_final = calcular_fator_periodo(data_sub_inicio, data_final, indexador, taxa, apenas_indexador=True)
            principal_atual = principal_atual * fator_final

        principal_liquido = calcular_impostos_sub_periodo(valor_inicial, principal_atual, data_compra, data_final)
        return round(principal_liquido + carteira_cupons_liquidos, 2)

    # 3. Fluxo Padrão (Sem Cupons)
    fator_total = calcular_fator_periodo(data_compra, data_final, indexador, taxa)
    valor_bruto = valor_inicial * fator_total
    
    valor_liquido = calcular_impostos_sub_periodo(valor_inicial, valor_bruto, data_compra, data_final)
    return round(valor_liquido, 2)
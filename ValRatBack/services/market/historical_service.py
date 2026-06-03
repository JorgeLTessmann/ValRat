# services/market/historical_service.py

import json
import os
import requests
from datetime import date, timedelta
from typing import Optional, Dict

# ========== CDI ==========
CACHE_FILE_CDI = "taxas_cdi_cache.json"

def _carregar_cache(caminho):
    if not os.path.exists(caminho):
        return {}
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def _salvar_cache(caminho, cache):
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2, ensure_ascii=False)

def buscar_cdi_mensal(ano: int, mes: int) -> Optional[float]:
    chave = f"{ano}-{mes:02d}"
    cache = _carregar_cache(CACHE_FILE_CDI)
    if chave in cache:
        return cache[chave]
    
    try:
        if mes == 12:
            data_fim = f"31/12/{ano}"
        else:
            ultimo_dia = (date(ano, mes+1, 1) - timedelta(days=1)).day
            data_fim = f"{ultimo_dia:02d}/{mes:02d}/{ano}"
        url = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.12/dados?formato=json&dataInicial=01/{mes:02d}/{ano}&dataFinal={data_fim}"
        resp = requests.get(url, timeout=30)
        if resp.status_code == 200:
            dados = resp.json()
            if dados:
                ultimo = dados[-1]
                valor_str = ultimo["valor"].replace(",", ".")
                taxa = float(valor_str) / 100
                cache[chave] = taxa
                _salvar_cache(CACHE_FILE_CDI, cache)
                return taxa
    except Exception as e:
        print(f"Erro CDI {chave}: {e}")
    return None

def buscar_taxas_cdi_periodo(data_inicio: date, data_fim: date) -> Dict[str, float]:
    taxas = {}
    ano = data_inicio.year
    mes = data_inicio.month
    while date(ano, mes, 1) <= data_fim:
        chave = f"{ano}-{mes:02d}"
        taxa = buscar_cdi_mensal(ano, mes)
        if taxa is None:
            taxa = 0.0085
        taxas[chave] = taxa
        if mes == 12:
            mes = 1
            ano += 1
        else:
            mes += 1
    return taxas

# ========== IPCA ==========
CACHE_FILE_IPCA = "taxas_ipca_cache.json"

def buscar_ipca_mensal(ano: int, mes: int) -> Optional[float]:
    chave = f"{ano}-{mes:02d}"
    cache = _carregar_cache(CACHE_FILE_IPCA)
    if chave in cache:
        return cache[chave]
    
    try:
        if mes == 12:
            data_fim = f"31/12/{ano}"
        else:
            ultimo_dia = (date(ano, mes+1, 1) - timedelta(days=1)).day
            data_fim = f"{ultimo_dia:02d}/{mes:02d}/{ano}"
        url = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.433/dados?formato=json&dataInicial=01/{mes:02d}/{ano}&dataFinal={data_fim}"
        resp = requests.get(url, timeout=30)
        if resp.status_code == 200:
            dados = resp.json()
            if dados:
                ultimo = dados[-1]
                valor_str = ultimo["valor"].replace(",", ".")
                taxa = float(valor_str) / 100
                cache[chave] = taxa
                _salvar_cache(CACHE_FILE_IPCA, cache)
                return taxa
    except Exception as e:
        print(f"Erro IPCA {chave}: {e}")
    return None

def buscar_taxas_ipca_periodo(data_inicio: date, data_fim: date) -> Dict[str, float]:
    taxas = {}
    ano = data_inicio.year
    mes = data_inicio.month
    while date(ano, mes, 1) <= data_fim:
        chave = f"{ano}-{mes:02d}"
        taxa = buscar_ipca_mensal(ano, mes)
        if taxa is None:
            taxa = 0.004
        taxas[chave] = taxa
        if mes == 12:
            mes = 1
            ano += 1
        else:
            mes += 1
    return taxas
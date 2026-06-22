# services/market/indicadores_service.py

"""
Serviço para busca de indicadores macroeconômicos históricos e atuais (CDI, SELIC, IPCA).
Usa BRAPI (macro endpoint) como motor principal e BrasilAPI como fallback rápido.
"""

import os
import requests
from datetime import date, datetime, timedelta
from typing import Optional, Dict, List
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN_BRAPI")

BASE_URL = "https://brapi.dev/api/v2/macro"


# =========================
# FUNÇÕES GENÉRICAS
# =========================

def _buscar_indicador(symbol: str, start_date: str, end_date: str = None) -> Optional[List[Dict]]:
    """
    Busca indicador macro da BRAPI.
    
    Args:
        symbol: 'cdi', 'selic', 'ipca', 'igpm', 'pib', etc.
        start_date: 'YYYY-MM-DD'
        end_date: 'YYYY-MM-DD' (opcional)
    """
    if end_date is None:
        end_date = date.today().strftime("%Y-%m-%d")
    
    url = f"{BASE_URL}?symbols={symbol}&startDate={start_date}&endDate={end_date}&token={TOKEN}"
    
    try:
        response = requests.get(url, timeout=30)
        if response.status_code != 200:
            print(f"[ERRO] BRAPI erro {response.status_code} para {symbol}")
            return None
        
        data = response.json()
        results = data.get("results", [])
        
        if not results:
            print(f"[AVISO] Sem resultados para {symbol}")
            return None
        
        return results
    
    except Exception as e:
        print(f"[ERRO] Erro ao buscar {symbol}: {e}")
        return None


# =========================
# CDI (Certificado de Depósito Interbancário)
# =========================

def buscar_cdi_historico(start_date: str = "1986-01-01", end_date: str = None) -> Optional[List[Dict]]:
    """
    Busca histórico do CDI.
    
    Args:
        start_date: Data inicial (padrão 1986-01-01)
        end_date: Data final (padrão hoje)
    
    Returns:
        Lista de dicionários com 'date' e 'value' (em %)
    """
    return _buscar_indicador("cdi", start_date, end_date)


def buscar_cdi_por_data(data: date) -> Optional[float]:
    """
    Busca a taxa CDI para uma data específica.
    Retorna valor em decimal (ex: 0.105 para 10.5%).
    """
    data_str = data.strftime("%Y-%m-%d")
    data_inicio = (data - timedelta(days=30)).strftime("%Y-%m-%d")
    
    resultados = _buscar_indicador("cdi", data_inicio, data_str)
    
    if resultados:
        for item in resultados:
            if item.get("date") == data_str:
                valor = item.get("value")
                if valor is not None:
                    return valor / 100
    
    return None


def buscar_cdi_mensal(ano: int, mes: int) -> Optional[float]:
    """
    Busca o CDI acumulado em um mês específico.
    Retorna valor em decimal (ex: 0.0105 para 1.05%).
    """
    data_inicio = f"{ano}-{mes:02d}-01"
    
    if mes == 12:
        data_fim = f"{ano}-12-31"
    else:
        ultimo_dia = (date(ano, mes + 1, 1) - timedelta(days=1)).day
        data_fim = f"{ano}-{mes:02d}-{ultimo_dia}"
    
    resultados = _buscar_indicador("cdi", data_inicio, data_fim)
    
    if resultados:
        ultimo = resultados[-1]
        valor = ultimo.get("value")
        if valor is not None:
            return valor / 100
    
    return None


# =========================
# SELIC (Taxa básica de juros)
# =========================

def buscar_selic_historico(start_date: str = "1986-01-01", end_date: str = None) -> Optional[List[Dict]]:
    """Busca histórico da SELIC"""
    return _buscar_indicador("selic", start_date, end_date)


def buscar_selic_por_data(data: date) -> Optional[float]:
    """Busca a taxa SELIC para uma data específica"""
    data_str = data.strftime("%Y-%m-%d")
    resultados = _buscar_indicador("selic", "2000-01-01", data_str)
    
    if resultados:
        for item in reversed(resultados):
            if item.get("date") <= data_str:
                valor = item.get("value")
                if valor is not None:
                    return valor / 100
    
    return None


# =========================
# IPCA (Índice de Preços ao Consumidor Amplo)
# =========================

def buscar_ipca_historico(start_date: str = "1980-01-01", end_date: str = None) -> Optional[List[Dict]]:
    """Busca histórico do IPCA"""
    return _buscar_indicador("ipca", start_date, end_date)


def buscar_ipca_por_data(data: date) -> Optional[float]:
    """Busca o IPCA acumulado nos últimos 12 meses para uma data"""
    data_str = data.strftime("%Y-%m-%d")
    resultados = _buscar_indicador("ipca", "2000-01-01", data_str)
    
    if resultados:
        for item in reversed(resultados):
            if item.get("date") <= data_str:
                valor = item.get("value")
                if valor is not None:
                    return valor / 100
    
    return None


def buscar_ipca_mensal(ano: int, mes: int) -> Optional[float]:
    """
    Busca o IPCA do mês específico (variação mensal).
    Retorna valor em decimal (ex: 0.0042 para 0.42%).
    """
    data_inicio = f"{ano}-{mes:02d}-01"
    
    if mes == 12:
        data_fim = f"{ano}-12-31"
    else:
        ultimo_dia = (date(ano, mes + 1, 1) - timedelta(days=1)).day
        data_fim = f"{ano}-{mes:02d}-{ultimo_dia}"
    
    resultados = _buscar_indicador("ipca", data_inicio, data_fim)
    
    if resultados:
        for item in resultados:
            if item.get("date") == data_fim:
                valor = item.get("value")
                if valor is not None:
                    return valor / 100
    
    return None


# =========================
# FUNÇÕES DE PERÍODO
# =========================

def buscar_cdi_periodo(data_inicio: date, data_fim: date) -> Dict[str, float]:
    """
    Busca todas as taxas CDI mensais entre duas datas.
    Retorna dict com chave 'YYYY-MM' e valor da taxa mensal.
    """
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


def buscar_ipca_periodo(data_inicio: date, data_fim: date) -> Dict[str, float]:
    """
    Busca todas as taxas IPCA mensais entre duas datas.
    Retorna dict com chave 'YYYY-MM' e valor do IPCA mensal.
    """
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


# =========================
# VALOR ATUAL (FALLBACK BRASILAPI)
# =========================

def get_cdi_atual() -> Optional[float]:
    """Retorna a taxa CDI mais recente buscando direto na BrasilAPI."""
    try:
        res = requests.get("https://brasilapi.com.br/api/taxas/v1/cdi", timeout=5)
        if res.status_code == 200:
            return float(res.json().get("valor", 0)) / 100
    except Exception as e:
        print(f"[AVISO] Falha no fallback BrasilAPI (CDI): {e}")
    return None


def get_selic_atual() -> Optional[float]:
    """Retorna a taxa SELIC mais recente buscando direto na BrasilAPI."""
    try:
        res = requests.get("https://brasilapi.com.br/api/taxas/v1/selic", timeout=5)
        if res.status_code == 200:
            return float(res.json().get("valor", 0)) / 100
    except Exception as e:
        print(f"[AVISO] Falha no fallback BrasilAPI (SELIC): {e}")
    return None


def get_ipca_atual() -> Optional[float]:
    """Tenta aproximar a última taxa IPCA via BRAPI."""
    try:
        # Usa o histórico do IPCA recente como proxy para o valor corrente
        hoje = date.today()
        inicio = (hoje - timedelta(days=60)).strftime("%Y-%m-%d")
        resultados = _buscar_indicador("ipca", inicio)
        if resultados:
            return float(resultados[-1].get("value", 0)) / 100
    except:
        pass
    return None

def buscar_taxa_cdi():
    return get_cdi_atual()
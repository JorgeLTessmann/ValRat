# services/market/taxa_cache_service.py

import json
import os
from datetime import date, datetime
from typing import Optional

# Caminho do arquivo JSON
CACHE_FILE = "taxas_cache.json"


def _carregar_cache() -> dict:
    """Carrega o arquivo JSON de cache"""
    if not os.path.exists(CACHE_FILE):
        return {"cdi": {}, "selic": {}, "ipca": {}}
    
    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _salvar_cache(cache: dict):
    """Salva o cache no arquivo JSON"""
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2, ensure_ascii=False)


def buscar_taxa_cache(tipo: str, data: date) -> Optional[float]:
    """
    Busca uma taxa no cache.
    Retorna None se não existir.
    """
    cache = _carregar_cache()
    data_str = data.strftime("%Y-%m-%d")
    
    return cache.get(tipo, {}).get(data_str)


def salvar_taxa_cache(tipo: str, data: date, valor: float):
    """
    Salva uma taxa no cache.
    """
    cache = _carregar_cache()
    data_str = data.strftime("%Y-%m-%d")
    
    if tipo not in cache:
        cache[tipo] = {}
    
    cache[tipo][data_str] = valor
    _salvar_cache(cache)
    print(f"💾 Taxa {tipo} para {data_str} salva no cache: {valor}")


def buscar_taxa_com_cache(tipo: str, data: date) -> Optional[float]:
    """
    Busca taxa primeiro no cache, depois na API se necessário.
    Se buscar da API, salva no cache automaticamente.
    """
    # 1. Tenta cache
    taxa = buscar_taxa_cache(tipo, data)
    if taxa is not None:
        print(f"📦 Cache hit: {tipo} {data} = {taxa}")
        return taxa
    
    # 2. Cache miss: busca da API
    print(f"🌐 Cache miss: buscando {tipo} {data} da API...")
    
    if tipo == "cdi":
        taxa = _buscar_cdi_api(data)
    elif tipo == "selic":
        taxa = _buscar_selic_api(data)
    elif tipo == "ipca":
        taxa = _buscar_ipca_api(data)
    else:
        return None
    
    # 3. Salva no cache e retorna
    if taxa is not None:
        salvar_taxa_cache(tipo, data, taxa)
    
    return taxa


def _buscar_cdi_api(data: date) -> Optional[float]:
    """
    Busca CDI de um mês específico via BACEN.
    """
    from services.market.bacen_service import buscar_serie_bacen
    
    # Série 12 do BACEN = CDI acumulado no mês
    dados = buscar_serie_bacen(12, data.strftime("%d/%m/%Y"))
    
    if not dados:
        return None
    
    # Procura o registro do mês
    for item in dados:
        item_data = datetime.strptime(item["data"], "%d/%m/%Y").date()
        if item_data.year == data.year and item_data.month == data.month:
            valor = float(item["valor"].replace(",", "."))
            return valor / 100  # converte percentual para decimal
    
    return None


def _buscar_selic_api(data: date) -> Optional[float]:
    """
    Busca SELIC de um mês específico via BACEN.
    """
    from services.market.bacen_service import buscar_serie_bacen
    
    # Série 11 do BACEN = SELIC acumulada no mês
    dados = buscar_serie_bacen(11, data.strftime("%d/%m/%Y"))
    
    if not dados:
        return None
    
    for item in dados:
        item_data = datetime.strptime(item["data"], "%d/%m/%Y").date()
        if item_data.year == data.year and item_data.month == data.month:
            valor = float(item["valor"].replace(",", "."))
            return valor / 100
    
    return None


def _buscar_ipca_api(data: date) -> Optional[float]:
    """
    Busca IPCA de um mês específico via BACEN.
    """
    from services.market.bacen_service import buscar_serie_bacen
    
    # Série 433 do BACEN = IPCA mensal
    dados = buscar_serie_bacen(433, data.strftime("%d/%m/%Y"))
    
    if not dados:
        return None
    
    for item in dados:
        item_data = datetime.strptime(item["data"], "%d/%m/%Y").date()
        if item_data.year == data.year and item_data.month == data.month:
            valor = float(item["valor"].replace(",", "."))
            return valor / 100
    
    return None


def buscar_taxa_mensal(tipo: str, ano: int, mes: int) -> Optional[float]:
    """
    Busca taxa de um mês/ano específico.
    """
    data = date(ano, mes, 1)
    return buscar_taxa_com_cache(tipo, data)


def preencher_cache_periodo(tipo: str, ano_inicio: int, ano_fim: int = None):
    """
    Pré-carrega o cache para um período inteiro.
    Útil para rodar uma vez e deixar tudo salvo.
    """
    if ano_fim is None:
        ano_fim = date.today().year
    
    total = 0
    for ano in range(ano_inicio, ano_fim + 1):
        for mes in range(1, 13):
            data = date(ano, mes, 1)
            if data > date.today():
                break
            
            taxa = buscar_taxa_com_cache(tipo, data)
            if taxa:
                total += 1
                print(f"✅ {tipo} {ano}-{mes:02d}: {taxa:.4f}")
    
    print(f"\n📊 Cache preenchido com {total} taxas {tipo}")
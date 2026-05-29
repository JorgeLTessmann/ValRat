import requests
from typing import Optional, List, Dict, Any
from datetime import datetime

BASE_URL = "https://brasilapi.com.br/api"


# =========================
# TAXAS (CDI, SELIC, IPCA)
# =========================

def buscar_taxas() -> Optional[Dict[str, Any]]:
    """
    Busca todas as taxas atuais (Selic, CDI, IPCA, IGPM, etc)
    """
    try:
        response = requests.get(
            f"{BASE_URL}/taxas/v1",
            timeout=15
        )
        
        if response.status_code != 200:
            return None
        
        return response.json()
    
    except Exception:
        return None


def buscar_taxa_selic() -> Optional[float]:
    """
    Busca apenas a taxa SELIC atual
    """
    taxas = buscar_taxas()
    
    if not taxas:
        return None
    
    for taxa in taxas:
        if taxa.get("nome") == "Selic":
            return taxa.get("valor")
    
    return None


def buscar_taxa_cdi() -> Optional[float]:
    """
    Busca apenas a taxa CDI atual
    """
    taxas = buscar_taxas()
    
    if not taxas:
        return None
    
    for taxa in taxas:
        if taxa.get("nome") == "CDI":
            return taxa.get("valor")
    
    return None


def buscar_taxa_ipca() -> Optional[float]:
    """
    Busca apenas a taxa IPCA atual
    """
    taxas = buscar_taxas()
    
    if not taxas:
        return None
    
    for taxa in taxas:
        if taxa.get("nome") == "IPCA":
            return taxa.get("valor")
    
    return None


# =========================
# TESOURO DIRETO
# =========================

def buscar_tesouro() -> Optional[List[Dict[str, Any]]]:
    """
    Busca todos os títulos do Tesouro Direto disponíveis
    """
    try:
        response = requests.get(
            f"{BASE_URL}/tesouro/v1",
            timeout=15
        )
        
        if response.status_code != 200:
            return None
        
        return response.json()
    
    except Exception:
        return None


def buscar_titulo_tesouro_por_codigo(codigo: str) -> Optional[Dict[str, Any]]:
    """
    Busca um título específico do Tesouro pelo código (ex: NTN-B 2035)
    """
    titulos = buscar_tesouro()
    
    if not titulos:
        return None
    
    for titulo in titulos:
        if titulo.get("codigo") == codigo.upper():
            return titulo
    
    return None


# =========================
# FUNDOS DE INVESTIMENTO (CVM)
# =========================

def buscar_fundos_cvm() -> Optional[List[Dict[str, Any]]]:
    """
    Busca todos os fundos de investimento cadastrados na CVM
    """
    try:
        response = requests.get(
            f"{BASE_URL}/cvm/fundos/v1",
            timeout=15
        )
        
        if response.status_code != 200:
            return None
        
        return response.json()
    
    except Exception:
        return None


def buscar_fundo_por_cnpj(cnpj: str) -> Optional[Dict[str, Any]]:
    """
    Busca um fundo específico pelo CNPJ
    """
    fundos = buscar_fundos_cvm()
    
    if not fundos:
        return None
    
    for fundo in fundos:
        if fundo.get("cnpj") == cnpj:
            return fundo
    
    return None


# =========================
# CDB (taxas referenciais)
# =========================

def buscar_taxas_cdb() -> Optional[List[Dict[str, Any]]]:
    """
    Busca taxas referenciais de CDB
    """
    try:
        response = requests.get(
            f"{BASE_URL}/cdb/v1",
            timeout=15
        )
        
        if response.status_code != 200:
            return None
        
        return response.json()
    
    except Exception:
        return None
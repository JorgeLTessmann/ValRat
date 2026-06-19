# services/market/treasury_service.py

import requests
from typing import Optional, List, Dict, Any

BASE_URL = "https://brasilapi.com.br/api"

def listar_titulos_tesouro() -> Optional[List[Dict[str, Any]]]:

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


def buscar_titulo(codigo: str) -> Optional[Dict[str, Any]]:

    titulos = listar_titulos_tesouro()
    
    if not titulos:
        return None
    
    for titulo in titulos:
        if titulo.get("codigo") == codigo.upper():
            return titulo
    
    return None


def get_preco_titulo(codigo: str) -> Optional[float]:

    titulo = buscar_titulo(codigo)
    
    if not titulo:
        return None
    
    return float(titulo.get("precoUnitario", 0))
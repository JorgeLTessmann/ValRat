# services/market/treasury_service.py

from services.market.brasilapi_service import (
    buscar_tesouro,
    buscar_titulo_tesouro_por_codigo
)


def listar_titulos_tesouro():
    """
    Lista todos os títulos do Tesouro Direto disponíveis
    """
    return buscar_tesouro()


def buscar_titulo(codigo: str):
    """
    Busca um título específico pelo código (ex: NTN-B 2035)
    """
    return buscar_titulo_tesouro_por_codigo(codigo)


def get_preco_titulo(codigo: str) -> float | None:
    """
    Retorna o preço atual de um título do Tesouro
    """
    titulo = buscar_titulo_tesouro_por_codigo(codigo)
    
    if not titulo:
        return None
    
    return titulo.get("precoUnitario")
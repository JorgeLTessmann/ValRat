# utils/market_utils.py

from datetime import date


def buscar_preco_por_data(historico, data):
    """
    Busca preço de um ativo em uma data específica.
    
    Args:
        historico: lista de dicionários com "date" e "price"
        data: data no formato YYYY-MM-DD ou date object
    
    Retorna:
        float | None = preço na data, ou None se não encontrar
    """
    
    # Normaliza data
    if hasattr(data, "strftime"):
        data_str = data.strftime("%Y-%m-%d")
    else:
        data_str = str(data)
    
    # Busca no histórico
    if not historico:
        return None
    
    for item in historico:
        if item.get("date") == data_str:
            return item.get("price")
    
    return None
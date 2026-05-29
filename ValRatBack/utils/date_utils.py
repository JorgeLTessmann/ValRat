# utils/date_utils.py

from datetime import datetime


def normalizar_data_compra(data):
    """
    Normaliza data de compra para string no formato YYYY-MM-DD.
    
    Aceita:
    - datetime object
    - string no formato YYYY-MM-DD
    - string no formato DD/MM/YYYY
    """
    
    if hasattr(data, "strftime"):
        return data.strftime("%Y-%m-%d")
    
    if isinstance(data, str):
        
        if "-" in data:
            partes = data.split("-")
            if len(partes) == 3:
                return data
        
        if "/" in data:
            partes = data.split("/")
            if len(partes) == 3:
                return f"{partes[2]}-{partes[1]}-{partes[0]}"
    
    return None
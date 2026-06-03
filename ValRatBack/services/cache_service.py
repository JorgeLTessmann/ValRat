# services/cache_service.py

from datetime import datetime, timedelta
from typing import Any, Optional

_cache = {}
_cache_timestamps = {}


def get_cache(key: str, max_age_seconds: int = 30) -> Optional[Any]:
    """
    Retorna valor do cache se ainda válido.
    
    Args:
        key: Chave do cache
        max_age_seconds: Idade máxima em segundos (padrão: 30)
    
    Returns:
        Valor armazenado ou None se expirado/inexistente
    """
    if key in _cache and key in _cache_timestamps:
        age = (datetime.now() - _cache_timestamps[key]).total_seconds()
        if age < max_age_seconds:
            print(f"📦 Cache hit: {key}")
            return _cache[key]
        else:
            print(f"⏰ Cache expired: {key}")
    return None


def set_cache(key: str, value: Any):
    """
    Armazena valor no cache.
    
    Args:
        key: Chave do cache
        value: Valor a ser armazenado
    """
    _cache[key] = value
    _cache_timestamps[key] = datetime.now()
    print(f"💾 Cache set: {key}")


def invalidate_cache(key: str = None):
    """
    Invalida cache específico ou todo.
    
    Args:
        key: Chave específica (None = limpa tudo)
    """
    if key:
        _cache.pop(key, None)
        _cache_timestamps.pop(key, None)
        print(f"🗑️ Cache invalidated: {key}")
    else:
        _cache.clear()
        _cache_timestamps.clear()
        print("🗑️ Cache completamente limpo")


def clear_cache():
    """Alias para invalidate_cache() sem argumentos"""
    invalidate_cache()
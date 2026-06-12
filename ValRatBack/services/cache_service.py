# services/cache_service.py

from datetime import datetime, timedelta
from typing import Any, Optional

_cache = {}
_cache_timestamps = {}


def get_cache(key: str, max_age_seconds: int = 30) -> Optional[Any]:
    """Retorna valor do cache se ainda válido"""
    if key in _cache and key in _cache_timestamps:
        age = (datetime.now() - _cache_timestamps[key]).total_seconds()
        if age < max_age_seconds:
            return _cache[key]
    return None


def set_cache(key: str, value: Any):
    """Armazena valor no cache"""
    _cache[key] = value
    _cache_timestamps[key] = datetime.now()


def invalidate_cache(key: str = None):
    """Invalida cache específico ou todo"""
    if key:
        _cache.pop(key, None)
        _cache_timestamps.pop(key, None)
    else:
        _cache.clear()
        _cache_timestamps.clear()
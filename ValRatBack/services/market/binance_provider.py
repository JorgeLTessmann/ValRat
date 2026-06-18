import requests
from datetime import datetime, timedelta, timezone
from typing import Optional

BASE_URL = "https://api1.binance.com/api/v3"

def buscar_preco_atual_cripto(symbol: str) -> Optional[float]:
    try:
        res = requests.get(f"{BASE_URL}/ticker/price", params={"symbol": f"{symbol.upper()}USDT"}, timeout=10)
        return float(res.json().get("price", 0)) if res.status_code == 200 else None
    except Exception as e:
        print(f"❌ Erro preço atual {symbol}: {e}")
        return None

def buscar_preco_historico_cripto(symbol: str, data_str: str) -> Optional[float]:
    try:
        dt = datetime.strptime(data_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        params = {
            "symbol": f"{symbol.upper()}USDT", 
            "interval": "1d",
            "startTime": int(dt.timestamp() * 1000),
            "endTime": int((dt + timedelta(days=1)).timestamp() * 1000), 
            "limit": 1
        }
        res = requests.get(f"{BASE_URL}/klines", params=params, timeout=10)
        data = res.json()
        return float(data[0][4]) if res.status_code == 200 and data else None
    except Exception as e:
        print(f"❌ Erro histórico {symbol}: {e}")
        return None

def buscar_historico_cripto_periodo(symbol: str, data_inicio: str, data_fim: str) -> list:
    try:
        inicio_ts = int(datetime.strptime(data_inicio, "%Y-%m-%d").timestamp() * 1000)
        fim_ts = int(datetime.strptime(data_fim, "%Y-%m-%d").timestamp() * 1000)
        
        params = {"symbol": f"{symbol.upper()}USDT", "interval": "1d", "startTime": inicio_ts, "endTime": fim_ts, "limit": 1000}
        res = requests.get(f"{BASE_URL}/klines", params=params, timeout=15)
        
        if res.status_code != 200: return []
        
        return [{
            "date": datetime.fromtimestamp(c[0] / 1000).strftime("%Y-%m-%d"),
            "open": float(c[1]), "high": float(c[2]), "low": float(c[3]), "close": float(c[4]), "volume": float(c[5])
        } for c in res.json()]
    except Exception as e:
        print(f"❌ Erro período {symbol}: {e}")
        return []

def buscar_preco_atual_cripto_brl(symbol: str) -> Optional[float]:
    from services.market.exchange_service import buscar_taxa_cambio_atual
    
    usdt = buscar_preco_atual_cripto(symbol)
    taxa = buscar_taxa_cambio_atual()
    return round(usdt * taxa, 2) if usdt and taxa else None

def buscar_preco_historico_cripto_brl(symbol: str, data_str: str) -> Optional[float]:
    from services.market.exchange_service import buscar_taxa_cambio_usd_brl
    
    usdt = buscar_preco_historico_cripto(symbol, data_str)
    dt = datetime.strptime(data_str, "%Y-%m-%d").date()
    taxa = buscar_taxa_cambio_usd_brl(dt)
    return round(usdt * taxa, 2) if usdt and taxa else None
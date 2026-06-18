import requests
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

BASE_URL = "https://api1.binance.com/api/v3"

# Mapeamento oficial para o CoinGecko localizar o ativo preciso
COINGECKO_MAP = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "LTC": "litecoin",
    "XRP": "ripple",
    "DOGE": "dogecoin",
    "ADA": "cardano",
    "SOL": "solana"
}

def buscar_preco_atual_cripto(symbol: str) -> Optional[float]:
    """Busca o preço em tempo real estrito da Binance (com fallback Coinbase se houver bloqueio de IP)."""
    try:
        res = requests.get(f"{BASE_URL}/ticker/price", params={"symbol": f"{symbol.upper()}USDT"}, timeout=7)
        if res.status_code == 200:
            return float(res.json().get("price", 0))
    except:
        pass

    try:
        res = requests.get(f"https://api.coinbase.com/v2/prices/{symbol.upper()}-USD/spot", timeout=5)
        if res.status_code == 200:
            return float(res.json()["data"]["amount"])
    except:
        return None

def buscar_preco_historico_cripto(symbol: str, data_str: str) -> Optional[float]:
    """
    Busca o preço histórico REAL usando a API pública do CoinGecko.
    Retorna None se o ativo não existia ou se a API falhar (Sem valores inventados).
    """
    try:
        coin_id = COINGECKO_MAP.get(symbol.upper(), symbol.lower())
        
        # Trata strings de data longas do frontend (ex: ISO timestamp)
        if "T" in data_str:
            data_str = data_str.split("T")[0]
            
        dt = datetime.strptime(data_str, "%Y-%m-%d")
        data_formatada = dt.strftime("%d-%m-%Y") # Formato estrito CoinGecko
        
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/history"
        res = requests.get(url, params={"date": data_formatada, "localization": "false"}, timeout=10)
        
        if res.status_code == 200:
            dados = res.json()
            if "market_data" in dados and "current_price" in dados["market_data"]:
                preco_real = float(dados["market_data"]["current_price"].get("usd", 0))
                return preco_real if preco_real > 0 else None
                
        return None # Retorna None se não achar o preço real
        
    except Exception as e:
        print(f"❌ Erro ao buscar preço real histórico de {symbol}: {e}")
        return None

def buscar_historico_cripto_periodo(symbol: str, data_inicio: str, data_fim: str) -> list:
    """Busca intervalo de preços reais históricos do CoinGecko para gráficos."""
    try:
        coin_id = COINGECKO_MAP.get(symbol.upper(), symbol.lower())
        start_ts = int(datetime.strptime(data_inicio, "%Y-%m-%d").timestamp())
        end_ts = int(datetime.strptime(data_fim, "%Y-%m-%d").timestamp())
        
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart/range"
        res = requests.get(url, params={"vs_currency": "usd", "from": start_ts, "to": end_ts}, timeout=12)
        
        if res.status_code == 200:
            prices = res.json().get("prices", [])
            return [{
                "date": datetime.fromtimestamp(p[0] / 1000, tz=timezone.utc).strftime("%Y-%m-%d"),
                "open": float(p[1]), "high": float(p[1]), "low": float(p[1]), "close": float(p[1]), "volume": 0.0
            } for p in prices]
    except:
        pass
    return []

def buscar_preco_atual_cripto_brl(symbol: str) -> Optional[float]:
    from services.market.exchange_service import buscar_taxa_cambio_atual
    usdt = buscar_preco_atual_cripto(symbol)
    taxa = buscar_taxa_cambio_atual()
    return round(usdt * taxa, 2) if usdt and taxa else None

def buscar_preco_historico_cripto_brl(symbol: str, data_str: str) -> Optional[float]:
    from services.market.exchange_service import buscar_taxa_cambio_usd_brl
    
    usdt = buscar_preco_historico_cripto(symbol, data_str)
    if not usdt:
        return None
        
    try:
        dt = datetime.strptime(data_str.split("T")[0], "%Y-%m-%d").date()
        taxa = buscar_taxa_cambio_usd_brl(dt)
        return round(usdt * taxa, 2) if taxa else None
    except:
        return None
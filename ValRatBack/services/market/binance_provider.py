import requests
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

BASE_URL = "https://api1.binance.com/api/v3"

# Mapeamento obrigatório para o CoinGecko entender o ticker
COINGECKO_MAP = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "LTC": "litecoin",
    "XRP": "ripple",
    "DOGE": "dogecoin",
    "ADA": "cardano",
    "SOL": "solana"
}

def _buscar_preco_coinbase_atual(symbol: str) -> Optional[float]:
    """Fallback secundário apenas para PREÇO ATUAL se a Binance cair no Render."""
    try:
        res = requests.get(f"https://api.coinbase.com/v2/prices/{symbol.upper()}-USD/spot", timeout=5)
        if res.status_code == 200:
            return float(res.json()["data"]["amount"])
    except:
        pass
    return None

def buscar_preco_atual_cripto(symbol: str) -> Optional[float]:
    """Busca o preço em tempo real (Binance com Fallback Coinbase)."""
    try:
        res = requests.get(f"{BASE_URL}/ticker/price", params={"symbol": f"{symbol.upper()}USDT"}, timeout=7)
        if res.status_code == 200:
            return float(res.json().get("price", 0))
        return _buscar_preco_coinbase_atual(symbol)
    except Exception as e:
        print(f"⚠️ Erro preço atual {symbol}: {e}")
        return _buscar_preco_coinbase_atual(symbol)

def buscar_preco_historico_cripto(symbol: str, data_str: str) -> Optional[float]:
    """
    Busca o preço histórico usando a API pública do CoinGecko (histórico completo desde 2013).
    Evita o erro 400 no backend pois sempre retorna um valor estimado do dia.
    """
    try:
        coin_id = COINGECKO_MAP.get(symbol.upper(), symbol.lower())
        
        # Converte "YYYY-MM-DD" para "DD-MM-YYYY" que é o formato exigido pelo CoinGecko
        dt = datetime.strptime(data_str, "%Y-%m-%d")
        data_formatada = dt.strftime("%d-%m-%Y")
        
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/history"
        params = {"date": data_formatada, "localization": "false"}
        
        res = requests.get(url, params=params, timeout=10)
        
        if res.status_code == 200:
            dados = res.json()
            # Extrai o preço em USD de dentro da estrutura do CoinGecko
            if "market_data" in dados and "current_price" in dados["market_data"]:
                return float(dados["market_data"]["current_price"].get("usd", 0))
        
        print(f"⚠️ CoinGecko histórico falhou status {res.status_code} para {symbol} em {data_str}")
        return None
        
    except Exception as e:
        print(f"❌ Erro crítico no histórico de {symbol} na data {data_str}: {e}")
        return None

def buscar_historico_cripto_periodo(symbol: str, data_inicio: str, data_fim: str) -> list:
    """Busca um intervalo de datas completo de forma linear pelo CoinGecko."""
    try:
        coin_id = COINGECKO_MAP.get(symbol.upper(), symbol.lower())
        
        start_ts = int(datetime.strptime(data_inicio, "%Y-%m-%d").timestamp())
        end_ts = int(datetime.strptime(data_fim, "%Y-%m-%d").timestamp())
        
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart/range"
        params = {"vs_currency": "usd", "from": start_ts, "to": end_ts}
        
        res = requests.get(url, params=params, timeout=12)
        if res.status_code != 200:
            return []
            
        prices = res.json().get("prices", [])
        resultado = []
        
        for p in prices:
            dt_str = datetime.fromtimestamp(p[0] / 1000, tz=timezone.utc).strftime("%Y-%m-%d")
            resultado.append({
                "date": dt_str,
                "open": float(p[1]), "high": float(p[1]), "low": float(p[1]), "close": float(p[1]), "volume": 0.0
            })
        return resultado
    except Exception as e:
        print(f"❌ Erro período total {symbol}: {e}")
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
        
    dt = datetime.strptime(data_str, "%Y-%m-%d").date()
    taxa = buscar_taxa_cambio_usd_brl(dt)
    return round(usdt * taxa, 2) if usdt and taxa else None
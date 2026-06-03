# services/market/binance_provider.py

import requests
from datetime import datetime, date, timedelta
from typing import Optional

BASE_URL = "https://api.binance.com/api/v3"


def buscar_preco_atual_cripto(symbol: str) -> Optional[float]:
    """
    Busca preço atual da criptomoeda na Binance.
    
    Args:
        symbol: 'BTC', 'ETH', 'SOL', 'ADA', 'XRP', etc.
    
    Returns:
        Preço em USDT (dólar americano)
    """
    try:
        url = f"{BASE_URL}/ticker/price"
        params = {"symbol": f"{symbol.upper()}USDT"}
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return float(data.get("price", 0))
        else:
            print(f"❌ Binance erro {response.status_code} para {symbol}")
            return None
    except Exception as e:
        print(f"❌ Erro ao buscar preço de {symbol}: {e}")
        return None


def buscar_preco_historico_cripto(symbol: str, data_str: str) -> Optional[float]:
    """
    Busca preço histórico da criptomoeda na Binance.
    
    Args:
        symbol: 'BTC', 'ETH', etc.
        data_str: Data no formato YYYY-MM-DD
    
    Returns:
        Preço de fechamento (último preço do dia)
    """
    try:
        data_busca = datetime.strptime(data_str, "%Y-%m-%d")
        data_inicio = int(data_busca.timestamp() * 1000)
        
        # Para o dia seguinte (busca candles do dia)
        data_fim = int((data_busca + timedelta(days=1)).timestamp() * 1000)
        
        url = f"{BASE_URL}/klines"
        params = {
            "symbol": f"{symbol.upper()}USDT",
            "interval": "1d",
            "startTime": data_inicio,
            "endTime": data_fim,
            "limit": 1
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data:
                # O preço de fechamento é o 4º elemento do candle
                return float(data[0][4])
        
        return None
    except Exception as e:
        print(f"❌ Erro ao buscar preço histórico de {symbol}: {e}")
        return None


def buscar_historico_cripto_periodo(symbol: str, data_inicio: str, data_fim: str) -> list:
    """
    Busca histórico de preços para um período.
    """
    try:
        inicio = datetime.strptime(data_inicio, "%Y-%m-%d")
        fim = datetime.strptime(data_fim, "%Y-%m-%d")
        
        inicio_ts = int(inicio.timestamp() * 1000)
        fim_ts = int(fim.timestamp() * 1000)
        
        url = f"{BASE_URL}/klines"
        params = {
            "symbol": f"{symbol.upper()}USDT",
            "interval": "1d",
            "startTime": inicio_ts,
            "endTime": fim_ts,
            "limit": 1000
        }
        
        response = requests.get(url, params=params, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            resultado = []
            for candle in data:
                resultado.append({
                    "date": datetime.fromtimestamp(candle[0] / 1000).strftime("%Y-%m-%d"),
                    "open": float(candle[1]),
                    "high": float(candle[2]),
                    "low": float(candle[3]),
                    "close": float(candle[4]),
                    "volume": float(candle[5])
                })
            return resultado
        return []
    except Exception as e:
        print(f"❌ Erro ao buscar histórico de {symbol}: {e}")
        return []
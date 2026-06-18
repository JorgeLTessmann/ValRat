# services/market/binance_provider.py

import requests
from datetime import datetime, date, timedelta, timezone
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
        # Binance usa candles diários abertos à meia-noite UTC
        data_busca = datetime.strptime(data_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        data_inicio = int(data_busca.timestamp() * 1000)
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


def buscar_preco_atual_cripto_brl(symbol: str) -> Optional[float]:
    """
    Busca o preço atual da criptomoeda em BRL com proteção contra erros.
    """
    from services.market.exchange_service import buscar_taxa_cambio_atual

    try:
        preco_usdt = buscar_preco_atual_cripto(symbol)
        if preco_usdt is None:
            return None

        taxa_cambio = buscar_taxa_cambio_atual()
        
        # Proteção contra retorno nulo do câmbio
        if taxa_cambio is None:
            print(f"❌ Não foi possível obter a taxa de câmbio atual para {symbol}")
            return None

        preco_brl = preco_usdt * taxa_cambio
        print(f"[CRIPTO BRL] {symbol}: ${preco_usdt:.2f} USDT * {taxa_cambio:.4f} = R$ {preco_brl:.2f}")
        return round(preco_brl, 2)
        
    except Exception as e:
        print(f"❌ Erro na conversão atual de BRL para {symbol}: {e}")
        return None


def buscar_preco_historico_cripto_brl(symbol: str, data_str: str) -> Optional[float]:
    """
    Busca o preço histórico da criptomoeda em BRL com proteção contra erros.
    """
    from services.market.exchange_service import buscar_taxa_cambio_usd_brl

    try:
        preco_usdt = buscar_preco_historico_cripto(symbol, data_str)
        if preco_usdt is None:
            return None

        data = datetime.strptime(data_str, "%Y-%m-%d").date()
        taxa_cambio = buscar_taxa_cambio_usd_brl(data)

        # Proteção contra retorno nulo do câmbio histórico (ex: finais de semana)
        if taxa_cambio is None:
            print(f"❌ Não foi possível obter a taxa de câmbio histórica em {data_str} para {symbol}")
            return None

        preco_brl = preco_usdt * taxa_cambio
        print(f"[CRIPTO HIST BRL] {symbol} em {data_str}: ${preco_usdt:.2f} USDT * {taxa_cambio:.4f} = R$ {preco_brl:.2f}")
        return round(preco_brl, 2)
        
    except Exception as e:
        print(f"❌ Erro na conversão histórica de BRL para {symbol} em {data_str}: {e}")
        return None
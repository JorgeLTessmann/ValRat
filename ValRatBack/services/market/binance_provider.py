import requests
from datetime import datetime, timedelta, timezone
from typing import Optional, List, Dict, Any

BASE_URL = "https://api1.binance.com/api/v3"

# Dicionário auxiliar para mapear símbolos para IDs do CoinGecko (essencial para dados antigos pré-2017)
COINGECKO_MAP = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "LTC": "litecoin",
    "XRP": "ripple",
    "DOGE": "dogecoin",
    "ADA": "cardano",
    "SOL": "solana"
}

def _buscar_preco_coinbase(symbol: str) -> Optional[float]:
    """Fallback robusto atual via Coinbase."""
    try:
        res = requests.get(f"https://api.coinbase.com/v2/prices/{symbol.upper()}-USD/spot", timeout=5)
        if res.status_code == 200:
            return float(res.json()["data"]["amount"])
    except Exception as e:
        print(f"⚠️ Fallback Coinbase Atual falhou para {symbol}: {e}")
    return None

def _buscar_preco_historico_coinbase(symbol: str, data_str: str) -> Optional[float]:
    """Fallback histórico via Coinbase que aceita parâmetros de data retroativa (Funciona em 2013/2016)."""
    try:
        # A Coinbase aceita o formato YYYY-MM-DD diretamente na URL query
        url = f"https://api.coinbase.com/v2/prices/{symbol.upper()}-USD/spot"
        res = requests.get(url, params={"date": data_str}, timeout=6)
        if res.status_code == 200:
            return float(res.json()["data"]["amount"])
    except Exception as e:
        print(f"⚠️ Fallback Histórico Coinbase falhou para {symbol} em {data_str}: {e}")
    return None

def _buscar_historico_coingecko_periodo(symbol: str, data_inicio: str, data_fim: str) -> List[Dict[str, Any]]:
    """Busca o histórico em lote do CoinGecko para períodos antigos onde a Binance não existia."""
    try:
        coin_id = COINGECKO_MAP.get(symbol.upper())
        if not coin_id:
            return []
            
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
        print(f"⚠️ Fallback de Período CoinGecko falhou: {e}")
        return []

def buscar_preco_atual_cripto(symbol: str) -> Optional[float]:
    """Busca preço atual com desvio imediato em caso de bloqueio no Render."""
    try:
        res = requests.get(f"{BASE_URL}/ticker/price", params={"symbol": f"{symbol.upper()}USDT"}, timeout=7)
        if res.status_code == 200:
            return float(res.json().get("price", 0))
        
        print(f"⚠️ Binance bloqueou ou falhou ({res.status_code}). Indo para Coinbase...")
        return _buscar_preco_coinbase(symbol)
    except Exception as e:
        print(f"❌ Erro Binance (Preço Atual): {e}. Acionando Coinbase...")
        return _buscar_preco_coinbase(symbol)

def buscar_preco_historico_cripto(symbol: str, data_str: str) -> Optional[float]:
    """Calcula se a data é anterior à criação da Binance e redireciona cirurgicamente o tráfego."""
    try:
        dt = datetime.strptime(data_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        
        # Inteligência Cronológica: Binance nasceu em Julho/2017. Datas retroativas vão direto para a Coinbase
        if dt.year < 2017 or (dt.year == 2017 and dt.month < 8):
            print(f"⏳ Data {data_str} é anterior à criação da Binance. Direcionando {symbol} para Coinbase Histórico...")
            return _buscar_preco_historico_coinbase(symbol, data_str)

        params = {
            "symbol": f"{symbol.upper()}USDT", 
            "interval": "1d",
            "startTime": int(dt.timestamp() * 1000),
            "endTime": int((dt + timedelta(days=1)).timestamp() * 1000), 
            "limit": 1
        }
        res = requests.get(f"{BASE_URL}/klines", params=params, timeout=10)
        
        if res.status_code == 200:
            data = res.json()
            if data and len(data) > 0:
                return float(data[0][4])  # Preço de Fechamento (Close)
                
        # Se a Binance retornar vazio (IP ban ou dados inexistentes de um par específico)
        print(f"⚠️ Binance não encontrou histórico para {symbol} em {data_str}. Acionando fallback...")
        return _buscar_preco_historico_coinbase(symbol, data_str)
        
    except Exception as e:
        print(f"❌ Erro histórico crítico na busca de {symbol}: {e}. Tentando salvar com Coinbase...")
        return _buscar_preco_historico_coinbase(symbol, data_str)

def buscar_historico_cripto_periodo(symbol: str, data_inicio: str, data_fim: str) -> list:
    """Busca o período completo tratando frentes híbridas (Binance + CoinGecko para dados históricos massivos)."""
    try:
        dt_inicio = datetime.strptime(data_inicio, "%Y-%m-%d")
        
        # Se o período começa antes de 2017, mude o lote inteiro para o CoinGecko
        if dt_inicio.year < 2017:
            print(f"⏳ Período antigo detectado ({data_inicio}). Coletando via CoinGecko...")
            return _buscar_historico_coingecko_periodo(symbol, data_inicio, data_fim)

        inicio_ts = int(dt_inicio.timestamp() * 1000)
        fim_ts = int(datetime.strptime(data_fim, "%Y-%m-%d").timestamp() * 1000)
        
        resultado = []
        atual_ts = inicio_ts

        while atual_ts < fim_ts:
            params = {
                "symbol": f"{symbol.upper()}USDT", 
                "interval": "1d", 
                "startTime": atual_ts, 
                "endTime": fim_ts, 
                "limit": 1000
            }
            res = requests.get(f"{BASE_URL}/klines", params=params, timeout=15)
            
            if res.status_code != 200:
                print(f"⚠️ Quebra de lote na Binance ({res.status_code}). Migrando lote restante para CoinGecko...")
                # Migração dinâmica caso o Render seja bloqueado no meio de um loop pesado
                data_atual_str = datetime.fromtimestamp(atual_ts / 1000).strftime("%Y-%m-%d")
                restante = _buscar_historico_coingecko_periodo(symbol, data_atual_str, data_fim)
                resultado.extend(restante)
                return resultado
            
            dados = res.json()
            if not dados: 
                break
            
            resultado.extend([{
                "date": datetime.fromtimestamp(c[0] / 1000, tz=timezone.utc).strftime("%Y-%m-%d"),
                "open": float(c[1]), "high": float(c[2]), "low": float(c[3]), "close": float(c[4]), "volume": float(c[5])
            } for c in dados])
            
            atual_ts = dados[-1][0] + 1
            
        return resultado
    except Exception as e:
        print(f"❌ Erro no processamento do período de {symbol}: {e}")
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
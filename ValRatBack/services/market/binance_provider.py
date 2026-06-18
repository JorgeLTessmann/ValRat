import requests
from datetime import datetime, timedelta, timezone
from typing import Optional

BASE_URL = "https://api1.binance.com/api/v3"  # Usando o subdomínio alternativo

def _buscar_preco_coinbase(symbol: str) -> Optional[float]:
    """Fallback caso a Binance bloqueie o IP do Render."""
    try:
        res = requests.get(f"https://api.coinbase.com/v2/prices/{symbol.upper()}-USD/spot", timeout=5)
        return float(res.json()["data"]["amount"]) if res.status_code == 200 else None
    except:
        return None

def buscar_preco_atual_cripto(symbol: str) -> Optional[float]:
    try:
        res = requests.get(f"{BASE_URL}/ticker/price", params={"symbol": f"{symbol.upper()}USDT"}, timeout=10)
        if res.status_code == 200:
            return float(res.json().get("price", 0))
        
        # Se der erro 418 ou qualquer outro na Binance, tenta a Coinbase
        print(f"⚠️ Binance falhou ({res.status_code}). Tentando Fallback Coinbase para {symbol}...")
        return _buscar_preco_coinbase(symbol)
    except Exception as e:
        print(f"❌ Erro preço atual Binance {symbol}: {e}. Tentando Coinbase...")
        return _buscar_preco_coinbase(symbol)

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
        # Converte as datas para o timestamp em milissegundos exigido pela Binance
        inicio_ts = int(datetime.strptime(data_inicio, "%Y-%m-%d").timestamp() * 1000)
        fim_ts = int(datetime.strptime(data_fim, "%Y-%m-%d").timestamp() * 1000)
        
        resultado = []
        atual_ts = inicio_ts

        # Loop em lotes caso o período seja maior que 1000 dias
        while atual_ts < fim_ts:
            params = {
                "symbol": f"{symbol.upper()}USDT", 
                "interval": "1d", 
                "startTime": atual_ts, 
                "endTime": fim_ts, 
                "limit": 1000
            }
            res = requests.get(f"{BASE_URL}/klines", params=params, timeout=15)
            if res.status_code != 200: break
            
            dados = res.json()
            if not dados: break  # Fim dos dados disponíveis
            
            # Formata e adiciona o lote atual ao resultado
            resultado.extend([{
                "date": datetime.fromtimestamp(c[0] / 1000).strftime("%Y-%m-%d"),
                "open": float(c[1]), "high": float(c[2]), "low": float(c[3]), "close": float(c[4]), "volume": float(c[5])
            } for c in dados])
            
            # O próximo lote começa 1 milissegundo após o último candle recebido
            atual_ts = dados[-1][0] + 1
            
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
    dt = datetime.strptime(data_str, "%Y-%m-%d").date()
    taxa = buscar_taxa_cambio_usd_brl(dt)
    return round(usdt * taxa, 2) if usdt and taxa else None
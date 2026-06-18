import requests
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any
import logging
import time

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────────────────────────
# MAPEAMENTOS
# ──────────────────────────────────────────────────────────────────────────────

# Mapeamento oficial para o CoinGecko localizar o ativo preciso
COINGECKO_MAP = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "LTC": "litecoin",
    "XRP": "ripple",
    "DOGE": "dogecoin",
    "ADA": "cardano",
    "SOL": "solana",
}

# Mapeamento para Kraken (usa símbolos diferentes)
KRAKEN_MAP = {
    "BTC": "XBTUSD",
    "ETH": "ETHUSD",
    "LTC": "LTCUSD",
    "XRP": "XXRPZUSD",
    "DOGE": "XDGUSD",
    "ADA": "ADAUSD",
    "SOL": "SOLUSD",
}

# Headers para evitar bloqueio por User-Agent
_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; portfolio-tracker/1.0)",
    "Accept": "application/json",
}

# ──────────────────────────────────────────────────────────────────────────────
# HELPERS INTERNOS
# ──────────────────────────────────────────────────────────────────────────────

def _get(url: str, params: dict = None, timeout: int = 8) -> Optional[requests.Response]:
    """GET com headers padrão e tratamento de erro unificado."""
    try:
        res = requests.get(url, params=params, headers=_HEADERS, timeout=timeout)
        if res.status_code == 200:
            return res
        logger.warning("HTTP %s em %s", res.status_code, url)
    except requests.RequestException as exc:
        logger.warning("Erro de rede em %s: %s", url, exc)
    return None


def _data_para_timestamp(data_str: str) -> int:
    """Converte 'YYYY-MM-DD' (ou ISO timestamp) para Unix timestamp (UTC)."""
    data_limpa = data_str.split("T")[0]
    dt = datetime.strptime(data_limpa, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    return int(dt.timestamp())


def _normalizar_data(data_str: str) -> str:
    """Garante formato YYYY-MM-DD a partir de qualquer string de data."""
    return data_str.split("T")[0]

# ──────────────────────────────────────────────────────────────────────────────
# PREÇO ATUAL  (Kraken → Bybit → CryptoCompare → Coinbase)
# Binance bloqueada em IPs europeus; removida da cadeia de fallback.
# ──────────────────────────────────────────────────────────────────────────────

def _preco_atual_kraken(symbol: str) -> Optional[float]:
    pair = KRAKEN_MAP.get(symbol.upper(), f"{symbol.upper()}USD")
    res = _get("https://api.kraken.com/0/public/Ticker", {"pair": pair})
    if res:
        data = res.json()
        if not data.get("error"):
            tickers = data.get("result", {})
            for ticker in tickers.values():
                return float(ticker["c"][0])  # "c" = last trade closed price
    return None


def _preco_atual_bybit(symbol: str) -> Optional[float]:
    res = _get(
        "https://api.bybit.com/v5/market/tickers",
        {"category": "spot", "symbol": f"{symbol.upper()}USDT"},
    )
    if res:
        data = res.json()
        lista = data.get("result", {}).get("list", [])
        if lista:
            return float(lista[0]["lastPrice"])
    return None


def _preco_atual_cryptocompare(symbol: str) -> Optional[float]:
    res = _get(
        "https://min-api.cryptocompare.com/data/price",
        {"fsym": symbol.upper(), "tsyms": "USD"},
    )
    if res:
        return float(res.json().get("USD", 0)) or None
    return None


def _preco_atual_coinbase(symbol: str) -> Optional[float]:
    res = _get(f"https://api.coinbase.com/v2/prices/{symbol.upper()}-USD/spot")
    if res:
        return float(res.json()["data"]["amount"])
    return None


def buscar_preco_atual_cripto(symbol: str) -> Optional[float]:
    """Busca o preço em tempo real da cripto em USD.
    Cadeia: Kraken → Bybit → CryptoCompare → Coinbase.
    (Binance bloqueada em servidores europeus — removida.)
    """
    for fonte in (_preco_atual_kraken, _preco_atual_bybit,
                  _preco_atual_cryptocompare, _preco_atual_coinbase):
        try:
            preco = fonte(symbol)
            if preco and preco > 0:
                logger.debug("Preço atual %s obtido via %s: %s", symbol, fonte.__name__, preco)
                return preco
        except Exception as exc:
            logger.warning("%s falhou para %s: %s", fonte.__name__, symbol, exc)

    logger.error("Nenhuma fonte retornou preço atual para %s", symbol)
    return None

# ──────────────────────────────────────────────────────────────────────────────
# PREÇO HISTÓRICO PONTUAL  (CryptoCompare → Kraken OHLC → CoinGecko)
# ──────────────────────────────────────────────────────────────────────────────

def _preco_historico_cryptocompare(symbol: str, data_str: str) -> Optional[float]:
    """CryptoCompare histoday: retorna OHLCV diário — usa 'close' como preço do dia."""
    ts = _data_para_timestamp(data_str)
    res = _get(
        "https://min-api.cryptocompare.com/data/v2/histoday",
        {"fsym": symbol.upper(), "tsym": "USD", "limit": 1, "toTs": ts},
    )
    if res:
        data = res.json()
        candles = data.get("Data", {}).get("Data", [])
        # Filtra candle cujo 'time' bate com o timestamp do dia solicitado
        for c in candles:
            diff = abs(c.get("time", 0) - ts)
            if diff < 86400 and c.get("close", 0) > 0:
                return float(c["close"])
    return None


def _preco_historico_kraken(symbol: str, data_str: str) -> Optional[float]:
    """Kraken OHLC com interval=1440 (1 dia). Busca o candle mais próximo."""
    pair = KRAKEN_MAP.get(symbol.upper(), f"{symbol.upper()}USD")
    ts_alvo = _data_para_timestamp(data_str)
    # Kraken precisa de 'since' = início do período; pedimos 2 dias antes para garantir
    since = ts_alvo - 86400 * 2
    res = _get(
        "https://api.kraken.com/0/public/OHLC",
        {"pair": pair, "interval": 1440, "since": since},
    )
    if res:
        data = res.json()
        if not data.get("error"):
            for values in data.get("result", {}).values():
                if isinstance(values, list):
                    for candle in values:
                        diff = abs(int(candle[0]) - ts_alvo)
                        if diff < 86400 * 2 and float(candle[4]) > 0:
                            return float(candle[4])  # índice 4 = close
    return None


def _preco_historico_coingecko(symbol: str, data_str: str) -> Optional[float]:
    """CoinGecko como último recurso (rate limit severo em IPs de cloud)."""
    coin_id = COINGECKO_MAP.get(symbol.upper(), symbol.lower())
    data_limpa = _normalizar_data(data_str)
    dt = datetime.strptime(data_limpa, "%Y-%m-%d")
    data_formatada = dt.strftime("%d-%m-%Y")

    res = _get(
        f"https://api.coingecko.com/api/v3/coins/{coin_id}/history",
        {"date": data_formatada, "localization": "false"},
        timeout=12,
    )
    if res:
        dados = res.json()
        preco = dados.get("market_data", {}).get("current_price", {}).get("usd", 0)
        return float(preco) if preco and float(preco) > 0 else None
    return None


def buscar_preco_historico_cripto(symbol: str, data_str: str) -> Optional[float]:
    """
    Busca o preço histórico REAL de uma cripto em USD para uma data específica.
    Cadeia: CryptoCompare → Kraken OHLC → CoinGecko.
    Retorna None se nenhuma fonte retornar valor (sem valores inventados).
    """
    for fonte in (_preco_historico_cryptocompare,
                  _preco_historico_kraken,
                  _preco_historico_coingecko):
        try:
            preco = fonte(symbol, data_str)
            if preco and preco > 0:
                logger.debug("Preço hist. %s em %s via %s: %s", symbol, data_str, fonte.__name__, preco)
                return preco
        except Exception as exc:
            logger.warning("%s falhou para %s em %s: %s", fonte.__name__, symbol, data_str, exc)

    logger.error("Nenhuma fonte retornou preço histórico para %s em %s", symbol, data_str)
    return None

# ──────────────────────────────────────────────────────────────────────────────
# HISTÓRICO EM PERÍODO  (CryptoCompare histoday → Kraken OHLC bulk)
# ──────────────────────────────────────────────────────────────────────────────

def _historico_periodo_cryptocompare(symbol: str, data_inicio: str, data_fim: str) -> list:
    ts_fim = _data_para_timestamp(data_fim)
    ts_ini = _data_para_timestamp(data_inicio)
    dias = max(1, (ts_fim - ts_ini) // 86400)

    res = _get(
        "https://min-api.cryptocompare.com/data/v2/histoday",
        {"fsym": symbol.upper(), "tsym": "USD", "limit": dias, "toTs": ts_fim},
    )
    if res:
        candles = res.json().get("Data", {}).get("Data", [])
        resultado = []
        for c in candles:
            ts = c.get("time", 0)
            if ts_ini <= ts <= ts_fim and c.get("close", 0) > 0:
                resultado.append({
                    "date": datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d"),
                    "open": float(c["open"]),
                    "high": float(c["high"]),
                    "low": float(c["low"]),
                    "close": float(c["close"]),
                    "volume": float(c.get("volumeto", 0)),
                })
        return resultado
    return []


def _historico_periodo_kraken(symbol: str, data_inicio: str, data_fim: str) -> list:
    pair = KRAKEN_MAP.get(symbol.upper(), f"{symbol.upper()}USD")
    ts_ini = _data_para_timestamp(data_inicio)
    ts_fim = _data_para_timestamp(data_fim)

    res = _get(
        "https://api.kraken.com/0/public/OHLC",
        {"pair": pair, "interval": 1440, "since": ts_ini - 86400},
    )
    if res:
        data = res.json()
        if not data.get("error"):
            resultado = []
            for values in data.get("result", {}).values():
                if isinstance(values, list):
                    for c in values:
                        ts = int(c[0])
                        if ts_ini <= ts <= ts_fim + 86400 and float(c[4]) > 0:
                            resultado.append({
                                "date": datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d"),
                                "open": float(c[1]),
                                "high": float(c[2]),
                                "low": float(c[3]),
                                "close": float(c[4]),
                                "volume": float(c[6]),
                            })
            return resultado
    return []


def buscar_historico_cripto_periodo(symbol: str, data_inicio: str, data_fim: str) -> list:
    """Busca intervalo de preços reais históricos para gráficos.
    Cadeia: CryptoCompare histoday → Kraken OHLC.
    Retorna lista de dicts com open/high/low/close/volume por dia.
    """
    for fonte in (_historico_periodo_cryptocompare, _historico_periodo_kraken):
        try:
            resultado = fonte(symbol, data_inicio, data_fim)
            if resultado:
                logger.debug(
                    "Histórico %s de %s a %s via %s: %d candles",
                    symbol, data_inicio, data_fim, fonte.__name__, len(resultado),
                )
                return resultado
        except Exception as exc:
            logger.warning("%s falhou para %s [%s→%s]: %s", fonte.__name__, symbol, data_inicio, data_fim, exc)

    logger.error("Nenhuma fonte retornou histórico para %s [%s→%s]", symbol, data_inicio, data_fim)
    return []

# ──────────────────────────────────────────────────────────────────────────────
# VERSÕES BRL  (delegam a exchange_service — sem alteração de interface)
# ──────────────────────────────────────────────────────────────────────────────

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
        dt = datetime.strptime(_normalizar_data(data_str), "%Y-%m-%d").date()
        taxa = buscar_taxa_cambio_usd_brl(dt)
        return round(usdt * taxa, 2) if taxa else None
    except Exception as exc:
        logger.warning("Erro ao converter para BRL (%s, %s): %s", symbol, data_str, exc)
        return None
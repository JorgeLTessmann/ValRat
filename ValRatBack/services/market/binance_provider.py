import datetime as datetime_module
import requests
from datetime import datetime, timezone, timedelta
from typing import Optional
import logging

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

# Mapeamento para Kraken (usa símbolos próprios)
KRAKEN_MAP = {
    "BTC": "XBTUSD",
    "ETH": "ETHUSD",
    "LTC": "LTCUSD",
    "XRP": "XXRPZUSD",
    "DOGE": "XDGUSD",
    "ADA": "ADAUSD",
    "SOL": "SOLUSD",
}

_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; portfolio-tracker/1.0)",
    "Accept": "application/json",
}

# ──────────────────────────────────────────────────────────────────────────────
# HELPERS INTERNOS
# ──────────────────────────────────────────────────────────────────────────────

def _get(url: str, params: dict = None, timeout: int = 8) -> Optional[requests.Response]:
    try:
        res = requests.get(url, params=params, headers=_HEADERS, timeout=timeout)
        print(f"[HTTP] {res.status_code} {url} params={params}")
        if res.status_code == 200:
            return res
        print(f"[HTTP ERRO] {res.status_code} body={res.text[:200]}")
    except requests.RequestException as exc:
        print(f"[NETWORK ERROR] {url} | {exc}")
    return None


def _normalizar_data(data_str) -> str:
    if isinstance(data_str, datetime_module.date):  # datetime herda de date, cobre ambos
        return data_str.strftime("%Y-%m-%d")
    return str(data_str).split("T")[0]


def _ts_inicio(data_str) -> int:
    """Retorna o Unix timestamp (UTC) do início do dia (00:00:00)."""
    data_limpa = _normalizar_data(data_str)
    dt = datetime.strptime(data_limpa, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    return int(dt.timestamp())


def _ts_fim(data_str) -> int:
    """Retorna o Unix timestamp (UTC) do início do dia SEGUINTE (limite exclusivo)."""
    data_limpa = _normalizar_data(data_str)
    dt = datetime.strptime(data_limpa, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    return int((dt + timedelta(days=1)).timestamp())

# ──────────────────────────────────────────────────────────────────────────────
# PREÇO ATUAL — cadeia: Kraken → Bybit → CryptoCompare → Coinbase
# Binance bloqueada em IPs europeus; removida da cadeia.
# ──────────────────────────────────────────────────────────────────────────────

def _preco_atual_kraken(symbol: str) -> Optional[float]:
    pair = KRAKEN_MAP.get(symbol.upper(), f"{symbol.upper()}USD")
    res = _get("https://api.kraken.com/0/public/Ticker", {"pair": pair})
    if res:
        data = res.json()
        if not data.get("error"):
            for ticker in data.get("result", {}).values():
                return float(ticker["c"][0])
    return None


def _preco_atual_bybit(symbol: str) -> Optional[float]:
    res = _get(
        "https://api.bybit.com/v5/market/tickers",
        {"category": "spot", "symbol": f"{symbol.upper()}USDT"},
    )
    if res:
        lista = res.json().get("result", {}).get("list", [])
        if lista:
            return float(lista[0]["lastPrice"])
    return None


def _preco_atual_cryptocompare(symbol: str) -> Optional[float]:
    res = _get(
        "https://min-api.cryptocompare.com/data/price",
        {"fsym": symbol.upper(), "tsyms": "USD"},
    )
    if res:
        preco = res.json().get("USD", 0)
        return float(preco) if preco else None
    return None


def _preco_atual_coinbase(symbol: str) -> Optional[float]:
    res = _get(f"https://api.coinbase.com/v2/prices/{symbol.upper()}-USD/spot")
    if res:
        return float(res.json()["data"]["amount"])
    return None


def buscar_preco_atual_cripto(symbol: str) -> Optional[float]:
    """Preço em tempo real em USD. Cadeia: Kraken → Bybit → CryptoCompare → Coinbase."""
    for fonte in (_preco_atual_kraken, _preco_atual_bybit,
                  _preco_atual_cryptocompare, _preco_atual_coinbase):
        try:
            preco = fonte(symbol)
            if preco and preco > 0:
                logger.info("[OK] Preço atual %s via %s: %s", symbol, fonte.__name__, preco)
                return preco
            logger.warning("[MISS] %s retornou %s para %s", fonte.__name__, preco, symbol)
        except Exception as exc:
            logger.warning("[ERRO] %s falhou para %s: %s", fonte.__name__, symbol, exc)
    logger.error("[FALHA TOTAL] Preço atual %s indisponível", symbol)
    return None

# ──────────────────────────────────────────────────────────────────────────────
# PREÇO HISTÓRICO PONTUAL
# Cadeia: CryptoCompare → CoinCap → Messari → Kraken → CoinGecko
#
# NOTA SOBRE toTs no CryptoCompare:
#   toTs = início do dia SOLICITADO (00:00 UTC) retorna candles do dia ANTERIOR.
#   toTs = início do dia SEGUINTE (00:00 UTC do dia+1) retorna o dia correto.
# ──────────────────────────────────────────────────────────────────────────────

def _preco_historico_cryptocompare(symbol: str, data_str: str) -> Optional[float]:
    """CryptoCompare histoday — preço de FECHAMENTO do dia. Dados desde 2010."""
    ts_alvo = _ts_inicio(data_str)
    ts_to = _ts_fim(data_str)  # início do dia SEGUINTE → inclui o dia solicitado

    res = _get(
        "https://min-api.cryptocompare.com/data/v2/histoday",
        {"fsym": symbol.upper(), "tsym": "USD", "limit": 1, "toTs": ts_to},
    )
    if res:
        candles = res.json().get("Data", {}).get("Data", [])
        logger.info("[CryptoCompare] candles retornados: %s", candles)
        for c in candles:
            diff = abs(c.get("time", 0) - ts_alvo)
            if diff < 86400 and c.get("close", 0) > 0:
                return float(c["close"])
    return None


def _preco_historico_coincap(symbol: str, data_str: str) -> Optional[float]:
    """CoinCap v2 — preço médio diário. Dados desde 2013, sem geo-block em EU."""
    coin_id = COINGECKO_MAP.get(symbol.upper(), symbol.lower())
    start_ms = _ts_inicio(data_str) * 1000
    end_ms = _ts_fim(data_str) * 1000

    res = _get(
        f"https://api.coincap.io/v2/assets/{coin_id}/history",
        {"interval": "d1", "start": start_ms, "end": end_ms},
        timeout=10,
    )
    if res:
        pontos = res.json().get("data", [])
        logger.info("[CoinCap] pontos retornados: %s", pontos)
        for p in pontos:
            preco = float(p.get("priceUsd", 0))
            if preco > 0:
                return preco
    return None


def _preco_historico_messari(symbol: str, data_str: str) -> Optional[float]:
    """Messari free tier — preço de FECHAMENTO. Dados desde 2011, sem geo-block."""
    data_limpa = _normalizar_data(data_str)
    data_fim = (datetime.strptime(data_limpa, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
    slug = COINGECKO_MAP.get(symbol.upper(), symbol.lower())

    res = _get(
        f"https://data.messari.io/api/v1/assets/{slug}/metrics/price/time-series",
        {"start": data_limpa, "end": data_fim, "interval": "1d"},
        timeout=10,
    )
    if res:
        values = res.json().get("data", {}).get("values", [])
        logger.info("[Messari] values retornados: %s", values)
        for v in values:
            # v = [timestamp_ms, open, high, low, close, volume]
            if len(v) >= 5 and v[4] and float(v[4]) > 0:
                return float(v[4])  # close
    return None


def _preco_historico_kraken(symbol: str, data_str: str) -> Optional[float]:
    """Kraken OHLC diário — preço de FECHAMENTO. Dados desde ~2014."""
    pair = KRAKEN_MAP.get(symbol.upper(), f"{symbol.upper()}USD")
    ts_alvo = _ts_inicio(data_str)
    since = ts_alvo - 86400 * 2  # 2 dias antes para garantir o candle do dia

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
    """CoinGecko — último recurso (rate limit severo em IPs de cloud). Dados desde 2013-04-28."""
    coin_id = COINGECKO_MAP.get(symbol.upper(), symbol.lower())
    data_limpa = _normalizar_data(data_str)
    data_formatada = datetime.strptime(data_limpa, "%Y-%m-%d").strftime("%d-%m-%Y")

    res = _get(
        f"https://api.coingecko.com/api/v3/coins/{coin_id}/history",
        {"date": data_formatada, "localization": "false"},
        timeout=12,
    )
    if res:
        dados = res.json()
        logger.info("[CoinGecko] resposta: %s", str(dados)[:300])
        preco = dados.get("market_data", {}).get("current_price", {}).get("usd", 0)
        return float(preco) if preco and float(preco) > 0 else None
    return None


def buscar_preco_historico_cripto(symbol: str, data_str: str) -> Optional[float]:
    """
    Preço de FECHAMENTO histórico em USD para uma data específica.
    Cadeia: CryptoCompare → CoinCap → Messari → Kraken → CoinGecko.
    Retorna None se nenhuma fonte retornar valor (sem valores inventados).
    """
    logger.info("[INICIO] buscar_preco_historico_cripto(%s, %s)", symbol, data_str)
    for fonte in (
        _preco_historico_cryptocompare,
        _preco_historico_coincap,
        _preco_historico_messari,
        _preco_historico_kraken,
        _preco_historico_coingecko,
    ):
        try:
            preco = fonte(symbol, data_str)
            if preco and preco > 0:
                logger.info("[OK] %s em %s via %s: %s USD", symbol, data_str, fonte.__name__, preco)
                return preco
            logger.warning("[MISS] %s retornou %s para %s em %s", fonte.__name__, preco, symbol, data_str)
        except Exception as exc:
            logger.warning("[ERRO] %s falhou para %s em %s: %s", fonte.__name__, symbol, data_str, exc)

    logger.error("[FALHA TOTAL] Preço histórico de %s em %s indisponível", symbol, data_str)
    return None

# ──────────────────────────────────────────────────────────────────────────────
# HISTÓRICO EM PERÍODO — cadeia: CryptoCompare → CoinCap → Kraken
# ──────────────────────────────────────────────────────────────────────────────

def _historico_periodo_cryptocompare(symbol: str, data_inicio: str, data_fim: str) -> list:
    ts_ini = _ts_inicio(data_inicio)
    ts_to = _ts_fim(data_fim)   # início do dia seguinte ao fim → inclui o último dia
    ts_fim_dia = _ts_inicio(data_fim)
    dias = max(1, (ts_fim_dia - ts_ini) // 86400)

    res = _get(
        "https://min-api.cryptocompare.com/data/v2/histoday",
        {"fsym": symbol.upper(), "tsym": "USD", "limit": dias, "toTs": ts_to},
    )
    if res:
        resultado = []
        for c in res.json().get("Data", {}).get("Data", []):
            ts = c.get("time", 0)
            if ts_ini <= ts <= ts_to and c.get("close", 0) > 0:
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


def _historico_periodo_coincap(symbol: str, data_inicio: str, data_fim: str) -> list:
    """CoinCap bulk — funciona para dados muito antigos (desde 2013)."""
    coin_id = COINGECKO_MAP.get(symbol.upper(), symbol.lower())
    start_ms = _ts_inicio(data_inicio) * 1000
    end_ms = _ts_fim(data_fim) * 1000

    res = _get(
        f"https://api.coincap.io/v2/assets/{coin_id}/history",
        {"interval": "d1", "start": start_ms, "end": end_ms},
        timeout=12,
    )
    if res:
        resultado = []
        for p in res.json().get("data", []):
            preco = float(p.get("priceUsd", 0))
            ts = int(p.get("time", 0)) // 1000
            if preco > 0:
                resultado.append({
                    "date": datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d"),
                    "open": preco, "high": preco, "low": preco, "close": preco, "volume": 0.0,
                })
        return resultado
    return []


def _historico_periodo_kraken(symbol: str, data_inicio: str, data_fim: str) -> list:
    pair = KRAKEN_MAP.get(symbol.upper(), f"{symbol.upper()}USD")
    ts_ini = _ts_inicio(data_inicio)
    ts_fim = _ts_fim(data_fim)

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
                        if ts_ini <= ts <= ts_fim and float(c[4]) > 0:
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
    """Histórico de preços para gráficos. Cadeia: CryptoCompare → CoinCap → Kraken.
    Retorna lista de dicts com open/high/low/close/volume por dia."""
    for fonte in (_historico_periodo_cryptocompare, _historico_periodo_coincap, _historico_periodo_kraken):
        try:
            resultado = fonte(symbol, data_inicio, data_fim)
            if resultado:
                logger.info("[OK] Histórico %s [%s→%s] via %s: %d candles",
                            symbol, data_inicio, data_fim, fonte.__name__, len(resultado))
                return resultado
            logger.warning("[MISS] %s retornou lista vazia para %s [%s→%s]",
                           fonte.__name__, symbol, data_inicio, data_fim)
        except Exception as exc:
            logger.warning("[ERRO] %s falhou para %s [%s→%s]: %s",
                           fonte.__name__, symbol, data_inicio, data_fim, exc)

    logger.error("[FALHA TOTAL] Histórico %s [%s→%s] indisponível", symbol, data_inicio, data_fim)
    return []

# ──────────────────────────────────────────────────────────────────────────────
# VERSÕES BRL — delegam a exchange_service (interface preservada)
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
        logger.warning("[ERRO BRL] %s %s: %s", symbol, data_str, exc)
        return None
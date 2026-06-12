# services/market/yahoo_provider.py

import yfinance as yf
from datetime import datetime, date, timedelta  # ← adicionar timedelta
from typing import Optional


def buscar_preco_historico_yahoo(ticker: str, data_str: str) -> Optional[float]:
    """
    Busca preço histórico via Yahoo Finance (fallback quando BRAPI falha).
    """
    try:
        ticker_yahoo = f"{ticker}.SA"
        data_fim = datetime.strptime(data_str, "%Y-%m-%d")
        data_ini = data_fim - timedelta(days=30)  # agora funciona
        
        ticker_obj = yf.Ticker(ticker_yahoo)
        hist = ticker_obj.history(start=data_ini, end=data_fim + timedelta(days=1))
        
        if hist.empty:
            return None
        
        return round(hist['Close'].iloc[-1], 2)
    except Exception as e:
        print(f"❌ Yahoo erro para {ticker}: {e}")
        return None


def buscar_preco_atual_yahoo(ticker: str) -> Optional[float]:
    """
    Busca preço atual via Yahoo Finance.
    """
    try:
        ticker_yahoo = f"{ticker}.SA"
        ticker_obj = yf.Ticker(ticker_yahoo)
        hist = ticker_obj.history(period="1d")
        
        if hist.empty:
            return None
        
        return round(hist['Close'].iloc[-1], 2)
    except Exception as e:
        print(f"❌ Yahoo erro para {ticker}: {e}")
        return None
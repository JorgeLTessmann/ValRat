"""
Serviço centralizado para busca de preços e rentabilidade.
Atende todos os tipos de ativos:
- Renda variável: busca da BRAPI (com histórico desde 1986) + fallback Yahoo Finance
- Renda fixa: usa calculadora própria
"""

import os
import requests
from datetime import datetime, date, timedelta
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN_BRAPI")


def _yahoo_preco_historico(ticker: str, data_str: str) -> Optional[float]:
    """Fallback via Yahoo Finance (converte para float nativo)"""
    try:
        from services.market.providers.yahoo_provider import buscar_preco_historico_yahoo
        preco = buscar_preco_historico_yahoo(ticker, data_str)
        if preco is not None:
            return float(preco)
    except Exception as e:
        print(f"Yahoo erro: {e}")
    return None


def _yahoo_preco_atual(ticker: str) -> Optional[float]:
    try:
        from services.market.providers.yahoo_provider import buscar_preco_atual_yahoo
        preco = buscar_preco_atual_yahoo(ticker)
        if preco is not None:
            return float(preco)
    except Exception:
        pass
    return None


def buscar_preco_historico_variavel(ticker: str, data_str: str) -> Optional[float]:
    data_busca = datetime.strptime(data_str, "%Y-%m-%d").date()
    hoje = date.today()
    if data_busca > hoje:
        return buscar_preco_atual_variavel(ticker)

    url = f"https://brapi.dev/api/quote/{ticker}?startDate=1986-01-01&endDate={data_str}&interval=1d&token={TOKEN}"
    try:
        resp = requests.get(url, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            results = data.get("results", [])
            if results:
                hist = results[0].get("historicalDataPrice", [])
                for item in hist:
                    item_date = datetime.fromtimestamp(item["date"]).strftime("%Y-%m-%d")
                    if item_date == data_str:
                        return float(item["close"])
                for item in reversed(hist):
                    if datetime.fromtimestamp(item["date"]).date() <= data_busca:
                        return float(item["close"])
    except Exception as e:
        print(f"BRAPI erro: {e}")

    return _yahoo_preco_historico(ticker, data_str)


def buscar_preco_atual_variavel(ticker: str) -> Optional[float]:
    url = f"https://brapi.dev/api/quote/{ticker}?token={TOKEN}"
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            results = data.get("results", [])
            if results:
                preco = results[0].get("regularMarketPrice")
                if preco:
                    return float(preco)
    except Exception:
        pass
    return _yahoo_preco_atual(ticker)


def calcular_valor_atual_fixa(
    valor_inicial: float,
    taxa_percentual: float,
    indexador: str,
    data_aplicacao_str: str,
    data_final_str: Optional[str] = None
) -> float:
    from services.renda_fixa.calculadora_renda_fixa import calcular_valor_renda_fixa
    return calcular_valor_renda_fixa(
        valor_inicial=valor_inicial,
        taxa=taxa_percentual,
        indexador=indexador,
        data_compra=data_aplicacao_str,
        data_final=data_final_str
    )


def buscar_cota_fundo(cnpj: str, data_str: Optional[str] = None) -> Optional[float]:
    url = f"https://brasilapi.com.br/api/cvm/fundos/v1/{cnpj}"
    try:
        resp = requests.get(url, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            cotas = data.get("cotas", [])
            if cotas:
                if data_str is None:
                    return cotas[0].get("cota")
                data_alvo = datetime.strptime(data_str, "%Y-%m-%d").date()
                for item in cotas:
                    item_data = datetime.strptime(item.get("data", ""), "%Y-%m-%d").date()
                    if item_data == data_alvo:
                        return item.get("cota")
    except Exception as e:
        print(f"Erro cota fundo: {e}")
    return None


def buscar_preco(
    tipo: str,
    codigo: str,
    data: Optional[str] = None
) -> Optional[float]:
    if tipo == "cripto":
        try:
            from services.market.binance_provider import (
                buscar_preco_atual_cripto_brl,
                buscar_preco_historico_cripto_brl
            )
            print(f"[DEBUG CRIPTO] tipo={tipo} codigo={codigo} data={data} data_type={type(data)}")
            if data:
                preco = buscar_preco_historico_cripto_brl(codigo, data)
                print(f"[DEBUG CRIPTO] preco retornado={preco}")
                if preco is None:
                    data_busca = datetime.strptime(data, "%Y-%m-%d").date()
                    if data_busca >= date.today():
                        preco = buscar_preco_atual_cripto_brl(codigo)
                return preco
            return buscar_preco_atual_cripto_brl(codigo)
        except Exception as e:
            print(f"[DEBUG CRIPTO] EXCEPTION: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return None

    if tipo in ["acao", "etf", "fii"]:
        if data:
            return buscar_preco_historico_variavel(codigo, data)
        return buscar_preco_atual_variavel(codigo)
    if tipo == "fundo":
        return buscar_cota_fundo(codigo, data)
    if tipo in ["cdb", "lci", "lca", "tesouro"]:
        return 1.0
    return None


def calcular_rentabilidade(
    tipo: str,
    preco_compra: float,
    quantidade: float,
    preco_atual: Optional[float] = None,
    codigo: Optional[str] = None
) -> Dict[str, Any]:
    valor_investido = preco_compra * quantidade
    if preco_atual is None and codigo and tipo:
        preco_atual = buscar_preco(tipo, codigo, None) or preco_compra
    valor_atual = preco_atual * quantidade
    lucro = valor_atual - valor_investido
    percentual = (lucro / valor_investido * 100) if valor_investido > 0 else 0
    return {
        "valor_investido": round(valor_investido, 2),
        "valor_atual": round(valor_atual, 2),
        "lucro": round(lucro, 2),
        "percentual": round(percentual, 2)
    }

def buscar_preco_atual_acao_fii(ticker: str):
    return buscar_preco_atual_variavel(ticker)


def buscar_preco_historico_acao_fii(ticker: str, data: str):
    return buscar_preco_historico_variavel(ticker, data)
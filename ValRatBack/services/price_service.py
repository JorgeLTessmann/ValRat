"""
Serviço centralizado para busca de preços e rentabilidade.
Atende todos os tipos de ativos:
- Renda variável: busca da BRAPI (com histórico desde 1986)
- Renda fixa: busca da BrasilAPI (taxas indexadoras)
"""

import os
import requests
from datetime import datetime, date, timedelta
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN_BRAPI")


# =========================
# UTILITÁRIOS
# =========================

def _data_eh_futura(data_str: str) -> bool:
    """Verifica se a data é futura"""
    try:
        data_busca = datetime.strptime(data_str, "%Y-%m-%d").date()
        hoje = date.today()
        return data_busca > hoje
    except:
        return False


def _converter_timestamp_para_str(timestamp):
    """Converte timestamp para string YYYY-MM-DD"""
    if isinstance(timestamp, (int, float)):
        return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d")
    return str(timestamp)[:10] if timestamp else ""


# =========================
# RENDA VARIÁVEL
# =========================

def buscar_preco_historico_variavel(ticker: str, data_str: str) -> Optional[float]:
    """
    Busca preço de fechamento de ação/FII/ETF em data específica.
    Usa BRAPI primeiro, fallback para Yahoo Finance.
    """
    data_busca = datetime.strptime(data_str, "%Y-%m-%d").date()
    hoje = date.today()
    
    if data_busca > hoje:
        print(f"⚠️ Data {data_str} é futura, usando preço atual para {ticker}")
        return buscar_preco_atual_variavel(ticker)
    
    # Define período: desde 1986 até a data buscada
    data_inicio = "1986-01-01"
    
    url = f"https://brapi.dev/api/quote/{ticker}?startDate={data_inicio}&endDate={data_str}&interval=1d&token={TOKEN}"
    
    try:
        response = requests.get(url, timeout=15)
        if response.status_code != 200:
            print(f"❌ BRAPI erro {response.status_code} para {ticker}")
            return _fallback_yahoo(ticker, data_str)
        
        data = response.json()
        results = data.get("results", [])
        if not results:
            print(f"❌ BRAPI sem resultados para {ticker}")
            return _fallback_yahoo(ticker, data_str)
        
        historical = results[0].get("historicalDataPrice", [])
        if not historical:
            print(f"⚠️ Histórico vazio para {ticker}, tentando Yahoo...")
            return _fallback_yahoo(ticker, data_str)
        
        # Busca o preço exato na data
        for item in historical:
            item_date = item.get("date")
            item_date_str = _converter_timestamp_para_str(item_date)
            
            if item_date_str == data_str:
                preco = item.get("close")
                if preco:
                    print(f"✅ Preço histórico {ticker} em {data_str}: R$ {preco}")
                    return preco
        
        # Se não encontrou exato, pega o mais próximo (anterior)
        for item in reversed(historical):
            item_date = item.get("date")
            item_date_str = _converter_timestamp_para_str(item_date)
            
            if item_date_str <= data_str:
                preco = item.get("close")
                if preco:
                    print(f"⚠️ Preço aproximado {ticker} em {data_str}: R$ {preco} (data mais próxima: {item_date_str})")
                    return preco
        
        # Fallback para Yahoo
        return _fallback_yahoo(ticker, data_str)
    
    except Exception as e:
        print(f"❌ Erro ao buscar preço histórico para {ticker}: {e}")
        return _fallback_yahoo(ticker, data_str)


def _fallback_yahoo(ticker: str, data_str: str) -> Optional[float]:
    """Fallback para Yahoo Finance quando BRAPI falha"""
    try:
        from services.market.yahoo_provider import buscar_preco_historico_yahoo
        preco = buscar_preco_historico_yahoo(ticker, data_str)
        if preco:
            print(f"✅ Yahoo fallback: {ticker} em {data_str} = R$ {preco}")
        return preco
    except Exception as e:
        print(f"❌ Yahoo fallback também falhou para {ticker}: {e}")
        return buscar_preco_atual_variavel(ticker)

def buscar_preco_atual_variavel(ticker: str) -> Optional[float]:
    """
    Busca preço atual de ação/FII/ETF via BRAPI.
    """
    url = f"https://brapi.dev/api/quote/{ticker}?token={TOKEN}"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            print(f"❌ BRAPI erro {response.status_code} para {ticker}")
            return None
        
        data = response.json()
        results = data.get("results", [])
        if not results:
            print(f"❌ BRAPI sem resultados para {ticker}")
            return None
        
        preco = results[0].get("regularMarketPrice")
        if preco is None:
            print(f"⚠️ Campo 'regularMarketPrice' não encontrado para {ticker}")
            return None
        
        return preco
    
    except Exception as e:
        print(f"❌ Erro ao buscar preço atual para {ticker}: {e}")
        return None


# =========================
# RENDA FIXA
# =========================

def calcular_valor_atual_fixa(
    valor_inicial: float,
    taxa_percentual: float,
    indexador: str,
    data_aplicacao_str: str,
    data_final_str: Optional[str] = None
) -> float:
    """
    Calcula o valor atual de um ativo de renda fixa com base no indexador.
    """
    from services.renda_fixa.calculadora_renda_fixa import calcular_valor_renda_fixa
    
    return calcular_valor_renda_fixa(
        valor_inicial=valor_inicial,
        taxa=taxa_percentual,
        indexador=indexador,
        data_compra=data_aplicacao_str,
        data_final=data_final_str
    )


# =========================
# FUNDOS (CVM)
# =========================

def buscar_cota_fundo(cnpj: str, data_str: Optional[str] = None) -> Optional[float]:
    """
    Busca a cota de um fundo de investimento pela BrasilAPI/CVM.
    Se data_str for fornecida, busca a cota mais próxima daquela data.
    """
    url = f"https://brasilapi.com.br/api/cvm/fundos/v1/{cnpj}"
    
    try:
        response = requests.get(url, timeout=15)
        if response.status_code != 200:
            return None
        
        data = response.json()
        cotas = data.get("cotas", [])
        
        if not cotas:
            return None
        
        if data_str is None:
            return cotas[0].get("cota")
        
        data_alvo = datetime.strptime(data_str, "%Y-%m-%d").date()
        
        for item in cotas:
            item_data = datetime.strptime(item.get("data", ""), "%Y-%m-%d").date()
            if item_data == data_alvo:
                return item.get("cota")
        
        return None
    
    except Exception as e:
        print(f"Erro ao buscar cota do fundo {cnpj}: {e}")
        return None


# =========================
# FUNÇÃO UNIVERSAL
# =========================

def buscar_preco(
    tipo: str,
    codigo: str,
    data: Optional[str] = None
) -> Optional[float]:
    """
    Função universal para buscar preço de qualquer tipo de ativo.
    
    Args:
        tipo: acao, etf, fii, cdb, lci, lca, fundo, tesouro
        codigo: ticker (para variável) ou CNPJ (para fundo) ou nome (para fixa)
        data: data no formato YYYY-MM-DD (opcional, se não informada retorna preço atual)
    
    Returns:
        Preço do ativo na data solicitada (ou atual se data=None)
    """
    
    # RENDA VARIÁVEL
    if tipo in ["acao", "etf", "fii"]:
        if data:
            return buscar_preco_historico_variavel(codigo, data)
        else:
            return buscar_preco_atual_variavel(codigo)
    
    # FUNDOS
    if tipo == "fundo":
        return buscar_cota_fundo(codigo, data)
    
    # RENDA FIXA (preço sempre 1, o valor é calculado com indexador)
    if tipo in ["cdb", "lci", "lca", "tesouro"]:
        return 1.0
    
    return None


def calcular_rentabilidade(
    tipo: str,
    preco_compra: float,
    quantidade: float,
    preco_atual: Optional[float] = None,
    codigo: Optional[str] = None,
    data_compra: Optional[str] = None
) -> Dict[str, Any]:
    """
    Calcula a rentabilidade de uma posição.
    
    Returns:
        {
            "valor_investido": float,
            "valor_atual": float,
            "lucro": float,
            "percentual": float
        }
    """
    valor_investido = preco_compra * quantidade
    
    if preco_atual is None and codigo and tipo:
        preco_atual = buscar_preco(tipo, codigo, None)
    
    if preco_atual is None:
        preco_atual = preco_compra
    
    valor_atual = preco_atual * quantidade
    lucro = valor_atual - valor_investido
    percentual = (lucro / valor_investido * 100) if valor_investido > 0 else 0
    
    return {
        "valor_investido": round(valor_investido, 2),
        "valor_atual": round(valor_atual, 2),
        "lucro": round(lucro, 2),
        "percentual": round(percentual, 2)
    }
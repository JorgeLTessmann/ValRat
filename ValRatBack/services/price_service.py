"""
Serviço centralizado para busca de preços e rentabilidade.
Atende todos os tipos de ativos:
- Renda variável: busca da BRAPI
- Renda fixa: busca da BrasilAPI (taxas indexadoras)
- Fundos: dados da CVM via BrasilAPI
"""

import os
import requests
from datetime import datetime, date
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN_BRAPI")

# =========================
# RENDA VARIÁVEL
# =========================

def buscar_preco_historico_variavel(ticker: str, data_str: str) -> Optional[float]:
    """
    Busca preço de fechamento de ação/FII/ETF em data específica.
    Usa o histórico da BRAPI (range de até 5 anos).
    """
    url = f"https://brapi.dev/api/quote/{ticker}?range=5y&interval=1d&token={TOKEN}"
    
    try:
        response = requests.get(url, timeout=15)
        if response.status_code != 200:
            return None
        
        data = response.json()
        results = data.get("results", [])
        if not results:
            return None
        
        historical = results[0].get("historicalDataPrice", [])
        if not historical:
            return None
        
        # Converte data alvo para timestamp
        data_alvo = datetime.strptime(data_str, "%Y-%m-%d").timestamp()
        
        # Encontra o preço mais recente anterior ou igual à data alvo
        preco_encontrado = None
        data_encontrada = 0
        
        for item in historical:
            item_date = item.get("date", 0)
            if item_date <= data_alvo and item_date > data_encontrada:
                data_encontrada = item_date
                preco_encontrado = item.get("close")
        
        return preco_encontrado
    
    except Exception as e:
        print(f"Erro ao buscar preço histórico para {ticker}: {e}")
        return None


def buscar_preco_atual_variavel(ticker: str) -> Optional[float]:
    """
    Busca preço atual de ação/FII/ETF via BRAPI.
    """
    url = f"https://brapi.dev/api/quote/{ticker}?token={TOKEN}"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return None
        
        data = response.json()
        results = data.get("results", [])
        if not results:
            return None
        
        return results[0].get("regularMarketPrice")
    
    except Exception as e:
        print(f"Erro ao buscar preço atual para {ticker}: {e}")
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
            # Pega a cota mais recente
            return cotas[0].get("cota")
        
        # Busca cota por data
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
        tipo: acao, etf, fii, cdb, lci, lca, fundo
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
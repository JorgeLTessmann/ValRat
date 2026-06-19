# services/asset_cache_service.py

"""
Serviço de cache de ativos em JSON.
Cria o arquivo automaticamente se não existir.
Popula dinamicamente conforme os usuários pesquisam.
"""

import json
import os
from typing import Optional, Dict, List
from datetime import datetime
import requests

CACHE_FILE = "ativos_cache.json"


# =========================
# FUNÇÕES DE BAIXO NÍVEL
# =========================

def _carregar_cache() -> dict:
    """Carrega o cache do arquivo JSON. Cria se não existir."""
    if not os.path.exists(CACHE_FILE):
        # Cria arquivo vazio automaticamente
        estrutura_inicial = {
            "cdi": {},
            "selic": {},
            "ipca": {},
            "ativos": {}
        }
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(estrutura_inicial, f, indent=2, ensure_ascii=False)
        return estrutura_inicial
    
    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _salvar_cache(cache: dict):
    """Salva o cache no arquivo JSON."""
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2, ensure_ascii=False)


# =========================
# FUNÇÕES PÚBLICAS
# =========================

def validar_ativo(ticker: str, tipo_selecionado: str) -> dict:
    """
    Valida se o ticker corresponde ao tipo selecionado.
    Busca no cache primeiro, depois na API se necessário.
    """
    ticker = ticker.upper()
    cache = _carregar_cache()
    ativos = cache.get("ativos", {})
    
    # 1. Tenta cache
    if ticker in ativos:
        ativo = ativos[ticker]
        tipo_real = ativo.get("tipo")
        nome = ativo.get("nome", ticker)
        preco_atual = ativo.get("preco_atual")
        
        print(f"📦 Cache hit: {ticker} -> tipo {tipo_real}")
        
        return {
            "valido": tipo_real == tipo_selecionado,
            "ticker": ticker,
            "nome": nome,
            "tipo_real": tipo_real,
            "preco_atual": preco_atual,
            "mensagem": f"✅ Ativo válido" if tipo_real == tipo_selecionado else f"❌ {ticker} é {tipo_real}, não {tipo_selecionado}"
        }
    
    # 2. Busca na API
    print(f"🌐 Cache miss: buscando {ticker} na BRAPI...")
    
    from dotenv import load_dotenv
    load_dotenv()
    TOKEN = os.getenv("TOKEN_BRAPI")
    
    url = f"https://brapi.dev/api/quote/{ticker}?token={TOKEN}"
    
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            return {
                "valido": False,
                "ticker": ticker,
                "nome": ticker,
                "tipo_real": None,
                "preco_atual": None,
                "mensagem": f"❌ Ativo {ticker} não encontrado na API"
            }
        
        data = response.json()
        results = data.get("results", [])
        
        if not results:
            return {
                "valido": False,
                "ticker": ticker,
                "nome": ticker,
                "tipo_real": None,
                "preco_atual": None,
                "mensagem": f"❌ Ativo {ticker} não encontrado na API"
            }
        
        resultado = results[0]
        nome = resultado.get("longName") or resultado.get("shortName") or ticker
        preco_atual = resultado.get("regularMarketPrice")
        
        # Inferência automática do tipo baseada nos dados da API
        tipo_real = _inferir_tipo(ticker, nome, resultado)
        
        # Salva no cache automaticamente
        ativos[ticker] = {
            "ticker": ticker,
            "nome": nome,
            "tipo": tipo_real,
            "preco_atual": preco_atual,
            "criado_em": datetime.now().isoformat()
        }
        cache["ativos"] = ativos
        _salvar_cache(cache)
        
        print(f"💾 Ativo {ticker} salvo no cache como {tipo_real}")
        
        return {
            "valido": tipo_real == tipo_selecionado,
            "ticker": ticker,
            "nome": nome,
            "tipo_real": tipo_real,
            "preco_atual": preco_atual,
            "mensagem": f"✅ Ativo válido" if tipo_real == tipo_selecionado else f"❌ {ticker} é {tipo_real}, não {tipo_selecionado}"
        }
    
    except Exception as e:
        print(f"❌ Erro ao validar {ticker}: {e}")
        return {
            "valido": False,
            "ticker": ticker,
            "nome": ticker,
            "tipo_real": None,
            "preco_atual": None,
            "mensagem": f"❌ Erro ao validar: {str(e)}"
        }


def _inferir_tipo(ticker: str, nome: str, dados_api: dict) -> str:
    """
    Infere o tipo do ativo com base em dados REAIS da API.
    Nada é mockado.
    """
    ticker = ticker.upper()
    nome = nome.upper()
    
    # 1. Por padrão do ticker
    if ticker.endswith("11") or "FII" in ticker or "FUNDO IMOBILIARIO" in nome:
        return "fii"
    
    if ticker.startswith(("BOVA", "IVVB", "SMAL", "GOLD", "HASH", "NSDV", "DIVO", "XINA", "ACWI")):
        return "etf"
    
    # 2. Pelos dados da API
    long_name = dados_api.get("longName", "").upper()
    
    if "ETF" in long_name or "FUNDO DE INDICE" in long_name:
        return "etf"
    
    if "FUNDO DE INVESTIMENTO IMOBILIARIO" in long_name:
        return "fii"
    
    if "FUNDO DE INVESTIMENTO" in long_name and "IMOBILIARIO" not in long_name:
        return "fundo"
    
    # 3. Padrão: ação
    return "acao"


def buscar_sugestoes(termo: str = "", limite: int = 10) -> List[Dict]:
    """
    Busca sugestões de ativos no cache (para autocomplete).
    Não chama API, só usa o que já foi salvo.
    """
    if not termo:
        return []
    
    cache = _carregar_cache()
    ativos = cache.get("ativos", {})
    termo = termo.upper()
    
    resultados = []
    
    for ticker, dados in ativos.items():
        if termo in ticker or termo in dados.get("nome", "").upper():
            resultados.append({
                "ticker": ticker,
                "nome": dados.get("nome", ticker),
                "tipo": dados.get("tipo")
            })
            if len(resultados) >= limite:
                break
    
    return resultados


def obter_tipo_ativo(ticker: str) -> Optional[str]:
    """
    Retorna o tipo de um ativo (usa cache ou API).
    """
    resultado = validar_ativo(ticker, "acao")
    
    if resultado.get("valido") is False and resultado.get("tipo_real") is None:
        return None
    
    return resultado.get("tipo_real")
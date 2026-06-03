# services/asset_validator_service.py

from typing import Dict, Any, List, Optional
from constants.asset_types import RENDA_VARIAVEL_TYPES, RENDA_FIXA_TYPES

# Lista de tickers conhecidos (para sugestões)
TICKERS_CONHECIDOS = {
    "acao": [
        "PETR4", "VALE3", "ITUB4", "BBDC4", "ABEV3", 
        "BBAS3", "WEGE3", "RENT3", "MGLU3", "VIIA3"
    ],
    "etf": [
        "BOVA11", "IVVB11", "SMAL11", "GOLD11", "HASH11", 
        "NSDV11", "DIVO11", "XINA11", "ACWI11", "BDRX11"
    ],
    "fii": [
        "HGLG11", "KNRI11", "MXRF11", "VISC11", "TORD11", 
        "HGRU11", "XPML11", "BRCR11", "IRDM11", "LVBI11"
    ],
    "cdb": ["CDB_INTER_110", "CDB_NUBANK_100", "CDB_BTG_105"],
    "lci": ["LCI_XP_92", "LCI_INTER_93", "LCI_BTG_91"],
    "lca": ["LCA_BTG_93", "LCA_INTER_94", "LCA_XP_90"],
    "tesouro": ["TESOURO_SELIC", "TESOURO_IPCA_2035", "TESOURO_PRE_2026"],
    "fundo": [],  # Será populado via API posteriormente
    "cripto": ["BTC", "ETH", "SOL", "ADA", "XRP"]  # Para quando implementar
}

# Lista de indexadores conhecidos
INDEXADORES_CONHECIDOS = ["CDI", "SELIC", "IPCA", "PRE"]

# Lista de plataformas conhecidas
PLATAFORMAS_CONHECIDAS = ["XP", "Inter", "Nubank", "BTG", "Clear", "Rico", "Modal", "Outro"]


def validar_tipo_ativo(tipo: str) -> Dict[str, Any]:
    """Valida se o tipo de ativo é suportado"""
    tipos_suportados = RENDA_VARIAVEL_TYPES + RENDA_FIXA_TYPES
    
    if tipo not in tipos_suportados:
        return {
            "valido": False,
            "erro": f"Tipo '{tipo}' não suportado. Tipos válidos: {', '.join(tipos_suportados)}",
            "sugestoes": tipos_suportados
        }
    
    return {"valido": True}


def validar_ticker(ticker: str, tipo: Optional[str] = None) -> Dict[str, Any]:
    """
    Valida se o ticker existe ou sugere opções próximas.
    """
    ticker = ticker.upper()
    
    if tipo and tipo in TICKERS_CONHECIDOS:
        conhecidos = TICKERS_CONHECIDOS[tipo]
        
        if ticker in conhecidos:
            return {"valido": True, "ticker": ticker}
        
        # Busca sugestões próximas
        sugestoes = [t for t in conhecidos if ticker in t or t in ticker]
        
        if sugestoes:
            return {
                "valido": False,
                "erro": f"'{ticker}' não encontrado. Você quis dizer: {', '.join(sugestoes[:3])}?",
                "sugestoes": sugestoes[:5]
            }
        
        return {
            "valido": False,
            "erro": f"'{ticker}' não está na lista de {tipo}s conhecidos. Verifique o código.",
            "exemplos": conhecidos[:5]
        }
    
    return {"valido": True, "ticker": ticker}  # Não temos lista para este tipo


def validar_plataforma(plataforma: str) -> Dict[str, Any]:
    """Valida a plataforma"""
    if plataforma.title() in PLATAFORMAS_CONHECIDAS:
        return {"valido": True, "plataforma": plataforma.title()}
    
    return {
        "valido": True,  # Aceita qualquer uma, mas sugere
        "plataforma": plataforma,
        "sugestao": "Considere usar uma plataforma conhecida: " + ", ".join(PLATAFORMAS_CONHECIDAS)
    }


def validar_indexador(indexador: str) -> Dict[str, Any]:
    """Valida o indexador para renda fixa"""
    indexador = indexador.upper()
    
    if indexador in INDEXADORES_CONHECIDOS:
        return {"valido": True, "indexador": indexador}
    
    return {
        "valido": False,
        "erro": f"Indexador '{indexador}' não reconhecido. Valores válidos: {', '.join(INDEXADORES_CONHECIDOS)}",
        "sugestoes": INDEXADORES_CONHECIDOS
    }


def buscar_sugestoes_ticker(tipo: str, termo: str = "") -> List[Dict[str, str]]:
    """
    Busca sugestões de tickers para autocomplete.
    """
    if tipo not in TICKERS_CONHECIDOS:
        return []
    
    termo = termo.upper()
    sugestoes = []
    
    for ticker in TICKERS_CONHECIDOS[tipo]:
        if termo in ticker or not termo:
            sugestoes.append({
                "ticker": ticker,
                "descricao": f"{tipo.upper()} - {ticker}"
            })
    
    return sugestoes[:10]


def obter_opcoes_tipo() -> List[Dict[str, Any]]:
    """
    Retorna todas as opções de tipo de ativo.
    """
    return [
        {"value": "acao", "label": "Ação", "icon": "📈", "description": "Ações de empresas brasileiras"},
        {"value": "etf", "label": "ETF", "icon": "📊", "description": "Fundos de índice"},
        {"value": "fii", "label": "FII", "icon": "🏢", "description": "Fundos Imobiliários"},
        {"value": "cdb", "label": "CDB", "icon": "💰", "description": "Certificado de Depósito Bancário"},
        {"value": "lci", "label": "LCI", "icon": "🏠", "description": "Letra de Crédito Imobiliário (Isento IR)"},
        {"value": "lca", "label": "LCA", "icon": "🌾", "description": "Letra de Crédito do Agronegócio (Isento IR)"},
        {"value": "tesouro", "label": "Tesouro Direto", "icon": "🏦", "description": "Títulos públicos federais"},
        {"value": "cripto", "label": "Criptomoeda", "icon": "₿", "description": "Bitcoin, Ethereum, etc"},
        {"value": "fundo", "label": "Fundo de Investimento", "icon": "📁", "description": "Fundos de investimento em geral"}
    ]


def obter_opcoes_indexador() -> List[Dict[str, Any]]:
    """
    Retorna opções de indexadores com descrição.
    """
    return [
        {"value": "CDI", "label": "CDI", "description": "Certificado de Depósito Interbancário"},
        {"value": "SELIC", "label": "SELIC", "description": "Taxa básica de juros"},
        {"value": "IPCA", "label": "IPCA", "description": "Índice de Preços ao Consumidor Amplo"},
        {"value": "PRE", "label": "Prefixado", "description": "Taxa fixa pré-determinada"}
    ]
# services/imposto_config_service.py

import json
import os
from typing import Dict, Any, Optional

_CONFIG_FILE = os.path.join(os.path.dirname(__file__), "..", "config", "imposto_config.json")


def _carregar_config() -> Dict[str, Any]:
    """Carrega a configuração de IR do arquivo JSON"""
    if not os.path.exists(_CONFIG_FILE):
        raise FileNotFoundError(f"Arquivo de configuração não encontrado: {_CONFIG_FILE}")
    
    with open(_CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _recarregar_config():
    """Força o recarregamento do cache (útil após editar o JSON)"""
    global _config_cache
    _config_cache = None


_config_cache = None


def _get_config() -> Dict[str, Any]:
    """Retorna a configuração com cache"""
    global _config_cache
    if _config_cache is None:
        _config_cache = _carregar_config()
    return _config_cache


def get_aliquota_ir_renda_fixa(dias: int) -> float:
    """
    Retorna a alíquota de IR para renda fixa baseada no prazo em dias.
    
    Args:
        dias: Número de dias entre compra e venda
    
    Returns:
        Alíquota em decimal (ex: 0.15 para 15%)
    """
    config = _get_config()
    regras = config.get("aliquotas_ir", {}).get("regras", [])
    
    for regra in regras:
        dias_min = regra.get("dias_min", 0)
        dias_max = regra.get("dias_max")
        
        if dias >= dias_min:
            if dias_max is None or dias <= dias_max:
                return regra.get("aliquota", 15.0) / 100
    
    return 0.15  # fallback


def is_ativo_isento(tipo_ativo: str) -> bool:
    """Verifica se o ativo é isento de IR"""
    config = _get_config()
    isentos = config.get("ativos_isentos_ir", {}).get("lista", [])
    return tipo_ativo.lower() in isentos


def get_aliquota_acao(day_trade: bool = False) -> float:
    """Retorna alíquota para ações"""
    config = _get_config()
    if day_trade:
        return config.get("acoes", {}).get("day_trade", 20.0) / 100
    return config.get("acoes", {}).get("swing_trade", 15.0) / 100


def get_aliquota_cripto(valor_vendido_mes: float = 0) -> float:
    """Retorna alíquota para criptomoedas"""
    config = _get_config()
    limite_isencao = config.get("criptomoedas", {}).get("limite_isencao_mensal", 35000)
    
    if valor_vendido_mes <= limite_isencao:
        return 0.0
    
    # Para valores maiores, usa a alíquota padrão
    return config.get("criptomoedas", {}).get("aliquota_padrao", 15.0) / 100


def get_aliquota_fundo_investimento() -> float:
    """Retorna alíquota para fundos de investimento"""
    config = _get_config()
    return config.get("fundos_investimento", {}).get("aliquota_padrao", 20.0) / 100


def get_versao_config() -> str:
    """Retorna a versão atual da configuração"""
    config = _get_config()
    return config.get("versoes", {}).get("atual", "desconhecida")


def get_data_vigencia() -> str:
    """Retorna a data de vigência da configuração"""
    config = _get_config()
    return config.get("versoes", {}).get("data_vigencia", "desconhecida")
# models/compra_model.py

from pydantic import BaseModel
from typing import Optional


class CompraModel(BaseModel):
    # Comuns
    categoria: str
    data_compra: str
    plataforma: str
    
    # Para renda variável/cripto
    ticker: Optional[str] = None
    quantidade: Optional[float] = None
    
    # Para renda fixa
    nome_aplicacao: Optional[str] = None
    valor_investido: Optional[float] = None
    data_vencimento: Optional[str] = None
    tem_carencia: Optional[bool] = False
    data_carencia: Optional[str] = None
    tipo_renda_fixa: Optional[str] = None  # 'cdb', 'lci', 'lca', 'tesouro'
    indexador: Optional[str] = None        # 'CDI', 'IPCA', 'PRE'
    taxa_contratada: Optional[float] = None
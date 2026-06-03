# models/compra_model.py

from pydantic import BaseModel
from typing import Optional


class CompraModel(BaseModel):
    categoria: str
    ticker: str
    data_compra: str
    quantidade: float
    plataforma: str
    tipo_renda_fixa: Optional[str] = None 
    valor_investido: Optional[float] = None
    taxa: Optional[float] = None
    indexador: Optional[str] = None
    data_vencimento: Optional[str] = None
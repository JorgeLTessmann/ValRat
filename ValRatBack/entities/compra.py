# entities/compra.py

from sqlalchemy import Column, Integer, String, Float
from database import Base


class Compra(Base):
    __tablename__ = "compras"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String)
    nome = Column(String)
    tipo = Column(String)
    categoria = Column(String, nullable=True)
    tipo_renda_fixa = Column(String, nullable=True)  
    plataforma = Column(String)
    quantidade = Column(Float)
    quantidade_original = Column(Float)
    quantidade_restante = Column(Float)
    preco_compra = Column(Float)
    data_compra = Column(String)
    valor_investido = Column(Float)
    valor_atual = Column(Float, nullable=True)
    taxa = Column(Float, nullable=True)
    indexador = Column(String, nullable=True)
    data_vencimento = Column(String, nullable=True)
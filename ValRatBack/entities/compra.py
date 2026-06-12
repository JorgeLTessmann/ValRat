# entities/compra.py

from sqlalchemy import Column, Integer, String, Float, Boolean, Date
from database import Base


class Compra(Base):
    __tablename__ = "compras"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String)
    nome = Column(String)
    tipo = Column(String)
    categoria = Column(String, nullable=True)  # 'variavel', 'fixa', 'cripto'
    
    # Campos existentes
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
    
    # NOVOS CAMPOS (para renda fixa)
    nome_aplicacao = Column(String, nullable=True)      # Nome do produto
    tem_carencia = Column(Boolean, default=False)      # Possui carência?
    data_carencia = Column(String, nullable=True)      # Data limite da carência
    tipo_renda_fixa = Column(String, nullable=True)    # 'cdb', 'lci', 'lca', 'tesouro'
    taxa_contratada = Column(Float, nullable=True)     # Taxa informada pelo usuário
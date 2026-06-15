# entities/transacao.py

from sqlalchemy import Column, Integer, ForeignKey, String, Float, DateTime
from database import Base
from datetime import datetime


class Transacao(Base):
    __tablename__ = "transacoes"

    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(String, nullable=False)  # 'compra', 'venda', 'dividendo', 'deposito', 'saque'
    ticker = Column(String, nullable=True)
    quantidade = Column(Float, nullable=True)
    preco = Column(Float, nullable=True)
    valor = Column(Float, nullable=False)
    data = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="success")  # 'success', 'pending', 'failed'
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
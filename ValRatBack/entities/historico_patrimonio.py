# entities/historico_patrimonio.py

from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from database import Base
from datetime import datetime


class HistoricoPatrimonio(Base):
    __tablename__ = "historico_patrimonio"

    id = Column(Integer, primary_key=True, index=True)
    # Adicionado: Vincula o registro do histórico ao usuário correto
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    
    patrimonio = Column(Float, nullable=False)
    investido = Column(Float, nullable=False)
    lucro = Column(Float, nullable=False)
    percentual = Column(Float, nullable=True)
    cdi = Column(Float, nullable=True)
    ibov = Column(Float, nullable=True)
    data = Column(DateTime, default=datetime.utcnow)
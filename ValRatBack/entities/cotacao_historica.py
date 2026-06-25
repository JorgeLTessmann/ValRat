# entities/cotacao_historica.py


from sqlalchemy import Column, Integer, String, Float, UniqueConstraint, Index
from database import Base


class CotacaoHistorica(Base):
    __tablename__ = "cotacao_historica"

    id = Column(Integer, primary_key=True, index=True)

    ticker = Column(String, nullable=False)
    tipo = Column(String, nullable=False)
    data = Column(String, nullable=False)
    preco = Column(Float, nullable=False)

    __table_args__ = (
        UniqueConstraint("ticker", "tipo", "data", name="uq_cotacao_ticker_tipo_data"),
        Index("ix_cotacao_busca", "ticker", "tipo", "data"),
    )
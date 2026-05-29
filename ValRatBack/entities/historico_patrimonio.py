from sqlalchemy import (
    Column,
    Integer,
    Float,
    DateTime
)

from database import Base

from datetime import datetime


class HistoricoPatrimonio(Base):

    __tablename__ = (
        "historico_patrimonio"
    )

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    patrimonio = Column(
        Float,
        nullable=False
    )

    investido = Column(
        Float,
        nullable=False
    )

    lucro = Column(
        Float,
        nullable=False
    )

    percentual = Column(
        Float,
        nullable=False
    )

    cdi = Column(
        Float,
        nullable=True
    )

    ibov = Column(
        Float,
        nullable=True
    )

    data = Column(
        DateTime,
        default=datetime.utcnow
    )
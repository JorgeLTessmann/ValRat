from sqlalchemy import (
    Column,
    Integer,
    String,
    Float
)

from database import Base


class RendaFixa(Base):

    __tablename__ = "renda_fixa"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    nome = Column(
        String,
        nullable=False
    )

    tipo = Column(
        String,
        nullable=False
    )

    indexador = Column(
        String,
        nullable=False
    )

    taxa = Column(
        Float,
        nullable=False
    )

    valor_aplicado = Column(
        Float,
        nullable=False
    )

    data_aplicacao = Column(
        String,
        nullable=False
    )

    data_vencimento = Column(
        String,
        nullable=False
    )

    liquidez = Column(
        String,
        nullable=True
    )

    emissor = Column(
        String,
        nullable=True
    )

    plataforma = Column(
        String,
        nullable=True
    )
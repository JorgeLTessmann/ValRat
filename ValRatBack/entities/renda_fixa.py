from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    ForeignKey  # Adicionado
)
from database import Base

class RendaFixa(Base):

    __tablename__ = "renda_fixa"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # =========================
    # RELACIONAMENTO
    # =========================
    usuario_id = Column(
        Integer,
        ForeignKey("usuarios.id"),
        nullable=False
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

    valor_applied = Column(  # Mantido conforme seu original (valor_aplicado)
        Float,
        name="valor_aplicado",
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
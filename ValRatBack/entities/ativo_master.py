from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    Date,
    Float
)

from database import Base


class AtivoMaster(Base):

    __tablename__ = "ativos_master"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # =========================
    # IDENTIFICAÇÃO
    # =========================

    codigo = Column(
        String,
        nullable=False,
        unique=True,
        index=True
    )

    nome = Column(
        String,
        nullable=False
    )

    tipo = Column(
        String,
        nullable=False,
        index=True
    )

    instituicao = Column(
        String,
        nullable=True
    )

    # =========================
    # CLASSIFICAÇÃO
    # =========================

    indexador = Column(
        String,
        nullable=True
    )

    fonte = Column(
        String,
        nullable=True
    )

    liquidez = Column(
        String,
        nullable=True
    )

    tributacao = Column(
        String,
        nullable=True
    )

    # =========================
    # DADOS FINANCEIROS
    # =========================

    taxa = Column(
        Float,
        nullable=True
    )

    percentual_indexador = Column(
        Float,
        nullable=True
    )

    vencimento = Column(
        Date,
        nullable=True
    )

    # =========================
    # CONTROLE
    # =========================

    ativo = Column(
        Boolean,
        default=True
    )
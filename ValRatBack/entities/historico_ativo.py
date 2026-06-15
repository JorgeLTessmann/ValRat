from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey  # Adicionado
)
from datetime import datetime
from database import Base

class HistoricoAtivo(Base):

    __tablename__ = (
        "historico_ativos"
    )

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

    ticker = Column(
        String,
        nullable=False
    )

    tipo = Column(
        String,
        nullable=False
    )

    preco = Column(
        Float,
        nullable=False
    )

    quantidade = Column(
        Float,
        nullable=False
    )

    valor_total = Column(
        Float,
        nullable=False
    )

    data_snapshot = Column(
        DateTime,
        default=datetime.utcnow
    )
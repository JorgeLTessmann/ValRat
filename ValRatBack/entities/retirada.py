from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    ForeignKey  # Adicionado
)
from database import Base

class Retirada(Base):

    __tablename__ = "retiradas"

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

    ticker = Column(String)

    valor = Column(Float)

    data = Column(String)
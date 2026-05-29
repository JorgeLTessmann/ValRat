from sqlalchemy import (
    Column,
    Integer,
    String,
    Float
)

from database import Base


class Retirada(Base):

    __tablename__ = "retiradas"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    ticker = Column(String)

    valor = Column(Float)

    data = Column(String)
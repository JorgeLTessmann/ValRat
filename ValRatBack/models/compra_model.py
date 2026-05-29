from pydantic import BaseModel

class CompraModel(BaseModel):

    ticker: str

    tipo: str

    quantidade: float

    data: str

    plataforma: str

    valor_investido: float | None = None

    taxa: float | None = None

    indexador: str | None = None

    data_vencimento: str | None = None
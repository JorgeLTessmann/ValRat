from pydantic import BaseModel


class RendaFixaModel(BaseModel):

    nome: str

    tipo: str

    indexador: str

    taxa: float

    valor_aplicado: float

    data_aplicacao: str

    data_vencimento: str

    liquidez: str | None = None

    emissor: str | None = None

    plataforma: str | None = None
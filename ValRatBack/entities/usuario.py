import hashlib
from database import Base
from sqlalchemy import Column, Integer, String

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    senha_hash = Column(String, nullable=False)

    @staticmethod
    def gerar_hash(senha: str) -> str:
        return hashlib.sha256(senha.encode('utf-8')).hexdigest()

    @classmethod
    def cadastrar(cls, db, nome: str, email: str, senha: str):
        if db.query(cls).filter(cls.email == email).first():
            return None
        novo = cls(nome=nome, email=email, senha_hash=cls.gerar_hash(senha))
        db.add(novo)
        db.commit()
        db.refresh(novo)
        return novo

    @classmethod
    def login(cls, db, email: str, senha: str):
        usuario = db.query(cls).filter(cls.email == email).first()
        if not usuario or usuario.senha_hash != cls.gerar_hash(senha):
            return None
        return usuario
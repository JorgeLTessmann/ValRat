# init_db.py

from database import Base, engine

# ENTIDADES
from entities.compra import Compra
from entities.renda_fixa import RendaFixa
from entities.historico_patrimonio import HistoricoPatrimonio
from entities.ativo_master import AtivoMaster
from entities.historico_ativo import HistoricoAtivo
from entities.retirada import Retirada

Base.metadata.create_all(bind=engine)

print("✅ Banco criado com sucesso.")
print("📋 Tabelas: ativos_master, compras, renda_fixa, historico_patrimonio, historico_ativos, retiradas")
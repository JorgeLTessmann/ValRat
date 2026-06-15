# init_db.py

from database import Base, engine
from entities.compra import Compra
from entities.renda_fixa import RendaFixa
from entities.historico_patrimonio import HistoricoPatrimonio
from entities.ativo_master import AtivoMaster
from entities.historico_ativo import HistoricoAtivo
from entities.retirada import Retirada
from entities.transacao import Transacao
from entities.usuario import Usuario

# Cria todas as tabelas com a estrutura mais recente
Base.metadata.create_all(bind=engine)

print("✅ Banco recriado com sucesso!")
print("📋 Tabelas criadas/atualizadas: compras, renda_fixa, historico_patrimonio, etc.")
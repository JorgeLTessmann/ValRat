# init_db.py (já está correto, apenas rode depois de alterar a entidade)

from database import Base, engine
from entities.compra import Compra
from entities.renda_fixa import RendaFixa
from entities.historico_patrimonio import HistoricoPatrimonio
from entities.ativo_master import AtivoMaster
from entities.historico_ativo import HistoricoAtivo
from entities.retirada import Retirada
from entities.transacao import Transacao

Base.metadata.create_all(bind=engine)
print("✅ Banco recriado com sucesso!")
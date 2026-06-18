import sys
import os
from datetime import datetime, timedelta, date
import calendar
import time

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
from entities.compra import Compra
from entities.historico_patrimonio import HistoricoPatrimonio

from services.brapi_service import buscar_ativo
from services.renda_fixa.calculadora_renda_fixa import calcular_valor_renda_fixa

def processar_usuario_historico(usuario_id: int):
    db = SessionLocal()
    print(f"\n[HISTÓRICO MENSAL] --- Iniciando sincronização para o Usuário ID: {usuario_id} ---")

    try:
        ultimo_registro = db.query(HistoricoPatrimonio)\
            .filter(HistoricoPatrimonio.usuario_id == usuario_id)\
            .order_by(HistoricoPatrimonio.data.desc())\
            .first()

        primeira_compra = db.query(Compra)\
            .filter(Compra.usuario_id == usuario_id)\
            .order_by(Compra.data_compra.asc())\
            .first()

        data_comercio_mais_antiga = None
        if primeira_compra:
            if isinstance(primeira_compra.data_compra, datetime):
                data_comercio_mais_antiga = primeira_compra.data_compra.date()
            elif isinstance(primeira_compra.data_compra, date):
                data_comercio_mais_antiga = primeira_compra.data_compra
            else:
                data_limpa = str(primeira_compra.data_compra).split(" ")[0]
                data_comercio_mais_antiga = datetime.strptime(data_limpa, "%Y-%m-%d").date()

        forcar_recalculo_total = False
        
        if ultimo_registro and data_comercio_mais_antiga:
            primeiro_registro_historico = db.query(HistoricoPatrimonio)\
                .filter(HistoricoPatrimonio.usuario_id == usuario_id)\
                .order_by(HistoricoPatrimonio.data.asc())\
                .first()
            
            if primeiro_registro_historico:
                if isinstance(primeiro_registro_historico.data, datetime):
                    data_inicio_real_historico = primeiro_registro_historico.data.date()
                elif isinstance(primeiro_registro_historico.data, date):
                    data_inicio_real_historico = primeiro_registro_historico.data
                else:
                    data_inicio_real_historico = datetime.strptime(str(primeiro_registro_historico.data), "%Y-%m-%d").date()

                if data_comercio_mais_antiga.replace(day=1) < data_inicio_real_historico.replace(day=1):
                    print(f"[HISTÓRICO ALERT] Compra retroativa detectada. Resetando histórico mensal...")
                    db.query(HistoricoPatrimonio).filter(HistoricoPatrimonio.usuario_id == usuario_id).delete()
                    db.commit()
                    forcar_recalculo_total = True
                    ultimo_registro = None

        if ultimo_registro and not forcar_recalculo_total:
            if isinstance(ultimo_registro.data, datetime):
                data_inicio = ultimo_registro.data.date()
            elif isinstance(ultimo_registro.data, date):
                data_inicio = ultimo_registro.data
            else:
                data_inicio = datetime.strptime(str(ultimo_registro.data), "%Y-%m-%d").date()
            
            if data_inicio.month == 12:
                data_inicio = date(data_inicio.year + 1, 1, 1)
            else:
                data_inicio = date(data_inicio.year, data_inicio.month + 1, 1)
        else:
            if data_comercio_mais_antiga:
                data_inicio = date(data_comercio_mais_antiga.year, data_comercio_mais_antiga.month, 1)
            else:
                data_inicio = date.today().replace(day=1)

        data_fim = date.today()

        if data_inicio > data_fim:
            print(f"[HISTÓRICO] O histórico mensal já está totalmente atualizado!")
            return

        compras_usuario = db.query(Compra).filter(Compra.usuario_id == usuario_id).all()
        if not compras_usuario:
            return

        precos_atuais = {}

        # Separa os tickers por categoria para buscar o preço correto
        compras_variavel_e_cripto = [
            c for c in compras_usuario
            if c.ticker and c.categoria not in ["Renda Fixa", "fixa"]
        ]
        tickers_por_categoria = {}
        for c in compras_variavel_e_cripto:
            tickers_por_categoria[c.ticker] = c.categoria or "variavel"

        for ticker, categoria in tickers_por_categoria.items():
            try:
                if categoria == "cripto":
                    from services.market.binance_provider import buscar_preco_atual_cripto_brl
                    preco = buscar_preco_atual_cripto_brl(ticker)
                    precos_atuais[ticker] = preco
                else:
                    dados_ticker = buscar_ativo(ticker)
                    if dados_ticker and "regularMarketPrice" in dados_ticker:
                        precos_atuais[ticker] = float(dados_ticker["regularMarketPrice"])
                    else:
                        precos_atuais[ticker] = None
                time.sleep(0.1)  # Evita block na API
            except Exception as e:
                print(f"[HISTÓRICO AVISO] Erro ao buscar preço de {ticker}: {e}")
                precos_atuais[ticker] = None

        ano_atual = data_inicio.year
        mes_atual = data_inicio.month
        snapshots_para_inserir = []

        while date(ano_atual, mes_atual, 1) <= data_fim.replace(day=1):
            ultimo_dia_do_mes = calendar.monthrange(ano_atual, mes_atual)[1]
            data_fechamento_mes = date(ano_atual, mes_atual, ultimo_dia_do_mes)
            
            if data_fechamento_mes > data_fim:
                data_fechamento_mes = data_fim

            patrimonio_dia = 0.0
            investido_dia = 0.0
            
            compras_ate_a_data = []
            for c in compras_usuario:
                if isinstance(c.data_compra, (datetime, date)):
                    data_c = c.data_compra.date() if isinstance(c.data_compra, datetime) else c.data_compra
                else:
                    data_c = datetime.strptime(str(c.data_compra).split(" ")[0], "%Y-%m-%d").date()
                if data_c <= data_fechamento_mes:
                    compras_ate_a_data.append(c)

            # 8. CÁLCULO DE RENDIMENTO PROGRESSIVO NO TEMPO
            for compra in compras_ate_a_data:
                # Caso de Renda Fixa
                if compra.categoria in ["Renda Fixa", "fixa"]:
                    valor_investido_ativo = compra.valor_investido or 0.0
                    investido_dia += valor_investido_ativo
                    
                    try:
                        taxa = compra.taxa_contratada if compra.taxa_contratada is not None else (compra.taxa or 0.0)
                        indexador = compra.indexador or "CDI"
                        tipo_rf = compra.tipo_renda_fixa or "cdb"
                        
                        valor_atual_ativo = calcular_valor_renda_fixa(
                            valor_inicial=valor_investido_ativo,
                            taxa=taxa,
                            indexador=indexador,
                            data_compra=compra.data_compra,
                            data_final=data_fechamento_mes,
                            tipo_ativo=tipo_rf
                        )
                    except Exception as ex:
                        print(f"[HISTÓRICO RF AVISO] Erro ao calcular Renda Fixa {compra.id}: {ex}")
                        valor_atual_ativo = valor_investido_ativo
                    
                    patrimonio_dia += valor_atual_ativo
                    continue

                # Caso de Renda Variável ou Cripto
                valor_investido_ativo = (compra.preco_compra * compra.quantidade) if (compra.preco_compra is not None and compra.quantidade is not None) else 0.0
                investido_dia += valor_investido_ativo

                preco_atual_mercado = precos_atuais.get(compra.ticker)
                if preco_atual_mercado is None or preco_atual_mercado == 0:
                    preco_atual_mercado = compra.preco_compra or 0.0

                # Calcula a variação total que o ativo teve da compra até hoje
                variacao_total = preco_atual_mercado / compra.preco_compra if (compra.preco_compra and compra.preco_compra > 0) else 1.0

                # Calcula quantos meses se passaram desde a compra até hoje
                if isinstance(compra.data_compra, (datetime, date)):
                    d_compra = compra.data_compra.date() if isinstance(compra.data_compra, datetime) else compra.data_compra
                else:
                    d_compra = datetime.strptime(str(compra.data_compra).split(" ")[0], "%Y-%m-%d").date()
                
                total_meses = (data_fim.year - d_compra.year) * 12 + (data_fim.month - d_compra.month)
                if total_meses <= 0:
                    total_meses = 1

                # Quantos meses se passaram desde a compra até o mês atual do loop
                meses_decorridos = (data_fechamento_mes.year - d_compra.year) * 12 + (data_fechamento_mes.month - d_compra.month)
                if meses_decorridos < 0:
                    meses_decorridos = 0

                # Aplica o rendimento de forma linear ao longo dos meses passados
                fator_tempo = meses_decorridos / total_meses
                fator_oscilacao_mes = 1.0 + ((variacao_total - 1.0) * fator_tempo)

                valor_atual_ativo = valor_investido_ativo * fator_oscilacao_mes
                patrimonio_dia += valor_atual_ativo

            if investido_dia > 0:
                lucro_dia = patrimonio_dia - investido_dia
                
                snapshot = HistoricoPatrimonio(
                    usuario_id=usuario_id,
                    data=data_fechamento_mes.strftime("%Y-%m-%d"),
                    patrimonio=patrimonio_dia,
                    investido=investido_dia,
                    lucro=lucro_dia
                )
                snapshots_para_inserir.append(snapshot)
            
            if mes_atual == 12:
                mes_atual = 1
                ano_atual += 1
            else:
                mes_atual += 1

        if snapshots_para_inserir:
            db.bulk_save_objects(snapshots_para_inserir)
            db.commit()
            print(f"[HISTÓRICO SUCESSO] {len(snapshots_para_inserir)} meses salvos com rendimento progressivo calculado.")
    except Exception as e:
        db.rollback()
        print(f"[HISTÓRICO ERRO CRÍTICO]: {str(e)}")
    finally:
        db.close()
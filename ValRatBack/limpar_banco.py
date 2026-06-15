# limpar_banco.py
from database import engine, Base
from sqlalchemy import text, inspect


def limpar_banco_literalmente():
    print("Iniciando varredura completa no banco de dados...")
    try:
        inspector = inspect(engine)
        tabelas = inspector.get_table_names()

        if not tabelas:
            print("O banco já está completamente vazio! Nenhuma tabela encontrada.")
            return

        print(f"Encontradas {len(tabelas)} tabelas: {', '.join(tabelas)}")
        print("Apagando todas com CASCADE (limpeza literal)...")

        with engine.connect() as connection:
            with connection.begin():
                for tabela in tabelas:
                    connection.execute(text(f"DROP TABLE IF EXISTS {tabela} CASCADE;"))
                    print(f"|-- Tabela '{tabela}' removida.")
                    
        print("\n💥 Banco limpo com sucesso absoluto! Tudo foi apagado.")
    except Exception as e:
        print(f"\n❌ Erro crítico ao limpar o banco: {e}")

if __name__ == "__main__":
    limpar_banco_literalmente()
from database import get_db, DocumentEmbedding, init_db
from sqlalchemy import text

def reset_embeddings():
    print("Iniciando limpeza da tabela de embeddings...")
    db = next(get_db())
    
    try:
        # Tentar truncar a tabela (mais rápido)
        db.execute(text("TRUNCATE TABLE document_embeddings RESTART IDENTITY CASCADE;"))
        db.commit()
        print("✅ Tabela document_embeddings limpa com sucesso!")
        
        # Opcional: Alterar a coluna se necessário, mas o SQLAlchemy deve lidar com isso no init_db se a tabela for recriada.
        # Como o pgvector define a dimensão na coluna, o ideal seria recriar a tabela se o truncate não resolver a dimensão da coluna,
        # mas vamos testar limpar primeiro. Se a coluna já foi criada com 3584, precisamos alterar a estrutura.
        
        print("Tentando ajustar a dimensão da coluna para 1536...")
        try:
             # Comando para alterar o tipo da coluna para vector(1536)
             db.execute(text("ALTER TABLE document_embeddings ALTER COLUMN embedding TYPE vector(1536);"))
             db.commit()
             print("✅ Dimensão da coluna ajustada para 1536.")
        except Exception as e:
            print(f"⚠️ Aviso ao alterar dimensão (pode já estar correta ou precisar de drop): {e}")

    except Exception as e:
        print(f"❌ Erro ao limpar tabela: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    reset_embeddings()

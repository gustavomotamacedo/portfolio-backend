"""
Script de diagnóstico para verificar embeddings no banco de dados
"""
import sys
import os

# Adicionar o diretório pai ao path para importar database
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import func
from database import get_db, DocumentEmbedding

def diagnosticar_banco():
    print("=" * 60)
    print("DIAGNÓSTICO DO BANCO DE DADOS - EMBEDDINGS")
    print("=" * 60)
    
    db = next(get_db())
    
    try:
        # 1. Contar total de embeddings
        total = db.query(DocumentEmbedding).count()
        print(f"\n📊 Total de embeddings no banco: {total}")
        
        # 2. Contar por source
        print("\n📁 Embeddings por arquivo (source):")
        sources = db.query(
            DocumentEmbedding.source,
            func.count(DocumentEmbedding.id).label('count')
        ).group_by(DocumentEmbedding.source).all()
        
        if not sources:
            print("   ⚠️  Nenhum embedding encontrado no banco!")
        else:
            for source, count in sources:
                print(f"   - {source}: {count} embeddings")
        
        # 3. Verificar especificamente o arquivo de hidrodinâmica
        print("\n🔍 Verificando 'potencial_hidrodinamica_completo.pdf':")
        hidro_count = db.query(DocumentEmbedding).filter(
            DocumentEmbedding.source == 'potencial_hidrodinamica_completo.pdf'
        ).count()
        
        if hidro_count > 0:
            print(f"   ✅ Encontrados {hidro_count} embeddings")
            
            # Mostrar exemplo de conteúdo
            sample = db.query(DocumentEmbedding).filter(
                DocumentEmbedding.source == 'potencial_hidrodinamica_completo.pdf'
            ).first()
            
            if sample:
                print(f"\n📄 Exemplo de conteúdo indexado:")
                print(f"   {sample.content[:200]}...")
        else:
            print(f"   ❌ Nenhum embedding encontrado para este arquivo!")
            print(f"\n💡 Possíveis causas:")
            print(f"   1. Arquivo não existe na pasta 'data/'")
            print(f"   2. Nome do arquivo está diferente")
            print(f"   3. Erro ao processar o PDF")
        
        # 4. Listar todos os sources disponíveis
        print("\n📋 Todos os arquivos indexados:")
        all_sources = db.query(DocumentEmbedding.source).distinct().all()
        if all_sources:
            for (source,) in all_sources:
                print(f"   - {source}")
        else:
            print("   Nenhum arquivo indexado!")
        
        print("\n" + "=" * 60)
        
    except Exception as e:
        print(f"\n❌ Erro ao diagnosticar banco: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    diagnosticar_banco()

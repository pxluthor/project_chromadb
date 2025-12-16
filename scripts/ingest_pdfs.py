#!/usr/bin/env python3
"""
Script para indexar PDFs no banco vetorial
"""
import sys
import argparse
from pathlib import Path

# Adiciona o diretório src ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import load_config
from src.pdf_extractor import PDFExtractor
from src.vectorstore import VectorStore


def main():
    parser = argparse.ArgumentParser(
        description="Indexa documentos PDF no banco vetorial ChromaDB"
    )
    
    parser.add_argument(
        "path",
        type=str,
        help="Caminho para arquivo PDF ou diretório com PDFs"
    )
    
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Procura PDFs em subdiretórios (apenas para diretórios)"
    )
    
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Limpa o banco vetorial antes de indexar"
    )
    
    parser.add_argument(
        "--collection",
        type=str,
        help="Nome da collection (sobrescreve configuração)"
    )
    
    args = parser.parse_args()
    
    try:
        print("="*80)
        print("🚀 INDEXAÇÃO DE DOCUMENTOS PDF")
        print("="*80)
        
        # Carrega configuração
        config = load_config()
        
        if args.collection:
            config.collection_name = args.collection
        
        print(f"\n📋 Configurações:")
        print(f"  Collection: {config.collection_name}")
        print(f"  Chunk size: {config.chunk_size}")
        print(f"  Chunk overlap: {config.chunk_overlap}")
        print(f"  Embedding model: {config.embedding_model}")
        
        # Inicializa componentes
        extractor = PDFExtractor()
        vectorstore = VectorStore(config)
        
        # Limpa banco se solicitado
        if args.clear:
            print(f"\n🗑️  Limpando banco vetorial...")
            vectorstore.clear_all_data()
            print("✓ Banco limpo")
        
        # Processa path
        path = Path(args.path)
        
        if not path.exists():
            print(f"\n❌ Erro: Caminho não encontrado: {path}")
            sys.exit(1)
        
        # Extrai documentos
        print(f"\n📄 Extraindo texto de: {path}")
        
        if path.is_file():
            if not path.suffix.lower() == '.pdf':
                print(f"❌ Erro: Arquivo não é PDF: {path}")
                sys.exit(1)
            pdf_documents = [extractor.extract_from_file(path)]
        else:
            pdf_documents = extractor.extract_from_directory(path, args.recursive)
        
        if not pdf_documents:
            print("❌ Nenhum documento foi extraído")
            sys.exit(1)
        
        print(f"✓ Extraídos {len(pdf_documents)} documento(s)")
        
        # Mostra resumo dos documentos
        print(f"\n📚 Documentos processados:")
        for i, doc in enumerate(pdf_documents, 1):
            print(f"  {i}. {doc.metadata['filename']}")
            print(f"     Páginas: {doc.total_pages} | Caracteres: {doc.total_characters:,}")
        
        # Indexa no vectorstore
        print(f"\n🗄️  Indexando no ChromaDB...")
        stats = vectorstore.add_documents(pdf_documents)
        
        # Mostra estatísticas
        print(f"\n{'='*80}")
        print("✅ INDEXAÇÃO CONCLUÍDA")
        print(f"{'='*80}")
        print(f"  Documentos processados: {stats['total_documents']}")
        print(f"  Total de páginas: {stats['total_pages']}")
        print(f"  Total de chunks: {stats['total_chunks']}")
        print(f"  Collection: {config.collection_name}")
        
        # Estatísticas da collection
        collection_stats = vectorstore.get_collection_stats()
        print(f"\n📊 Estatísticas da Collection:")
        print(f"  Total de chunks no banco: {collection_stats['total_chunks']}")
        print(f"  Documentos únicos: {collection_stats['unique_sources']}")
        
        if collection_stats['sources']:
            print(f"  Fontes:")
            for source in collection_stats['sources']:
                print(f"    - {source}")
        
        print(f"\n✓ Use 'python chat.py' para conversar com os documentos")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Indexação cancelada pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
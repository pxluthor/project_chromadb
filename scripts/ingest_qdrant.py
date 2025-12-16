import sys
import os
import time
from pathlib import Path
from typing import List

# Adiciona o diretório raiz ao path para importar os módulos src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.config import Config, load_config
from src.vectorstore import VectorStore
from src.pdf_extractor import PDFExtractor, PDFDocument

def main():
    # 1. Carrega Configurações
    try:
        config = load_config()
    except Exception as e:
        print(f"❌ Erro ao carregar configurações: {e}")
        return

    # ============================================================
    # 🚨 FORÇAR PROVEDOR QDRANT
    # ============================================================
    config.vector_store_provider = "qdrant"
    
    print("\n" + "="*50)
    print(f"🚀 INICIANDO INGESTÃO PARA O QDRANT SERVER")
    print(f"🎯 Alvo: {config.qdrant_host}:{config.qdrant_port}")
    print(f"📁 Coleção: {config.collection_name}")
    print("="*50 + "\n")

    # 2. Inicializa o Vector Store
    try:
        vs = VectorStore(config)
    except Exception as e:
        print(f"❌ Falha ao conectar no Qdrant: {e}")
        return

    # 3. Localiza PDFs
    data_dir = config.data_dir
    if not data_dir.exists():
        print(f"❌ Diretório de dados não encontrado: {data_dir}")
        return

    # Lógica de fallback para diretório de PDFs
    pdfs_dir = config.pdfs_dir if hasattr(config, 'pdfs_dir') else data_dir
    files_source = pdfs_dir if pdfs_dir.exists() else data_dir
    
    pdf_files = list(files_source.glob("*.pdf"))
    
    if not pdf_files:
        print(f"⚠️ Nenhum arquivo PDF encontrado em {files_source}")
        return

    print(f"📄 Encontrados {len(pdf_files)} arquivos PDF em '{files_source.name}' para processar.\n")

    # 4. Processa PDFs (Extração de Texto)
    extractor = PDFExtractor()
    documents_to_ingest: List[PDFDocument] = []

    for i, pdf_path in enumerate(pdf_files, 1):
        print(f"[{i}/{len(pdf_files)}] Lendo: {pdf_path.name}...", end=" ", flush=True)
        try:
            # --- CORREÇÃO AQUI: load_pdf -> extract_from_file ---
            doc = extractor.extract_from_file(pdf_path)
            
            if doc:
                documents_to_ingest.append(doc)
                print(f"✅ ({doc.total_pages} páginas)")
            else:
                print("⚠️ Ignorado (vazio ou ilegível)")
        except Exception as e:
            print(f"❌ Erro: {e}")

    if not documents_to_ingest:
        print("\n❌ Nenhum documento válido para ingestão.")
        return

    # 5. Envia para o Qdrant
    print(f"\n💾 Iniciando upload de {len(documents_to_ingest)} documentos para o Qdrant...")
    print("⏳ Isso pode levar alguns instantes (geração de embeddings + upload rede)...")
    
    start_time = time.time()
    
    try:
        stats = vs.add_documents(documents_to_ingest)
        
        elapsed = time.time() - start_time
        
        print("\n" + "="*50)
        print("✅ INGESTÃO CONCLUÍDA COM SUCESSO!")
        print("="*50)
        print(f"⏱️  Tempo total: {elapsed:.2f} segundos")
        print(f"📚 Documentos: {stats['total_documents']}")
        print(f"🧩 Chunks criados: {stats['total_chunks']}")
        print(f"🔌 Backend usado: Qdrant ({config.qdrant_host})")
        print("="*50)

    except Exception as e:
        print(f"\n❌ Erro crítico durante a ingestão no Qdrant: {e}")

if __name__ == "__main__":
    main()
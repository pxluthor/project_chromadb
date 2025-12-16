#!/usr/bin/env python3
"""
Script para diagnosticar problemas na API
"""
import sys
from pathlib import Path

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

def check_file_exists(filepath: str) -> bool:
    """Verifica se arquivo existe"""
    exists = Path(filepath).exists()
    status = "✅" if exists else "❌"
    print(f"{status} {filepath}")
    return exists

def check_import(module_path: str, name: str) -> bool:
    """Verifica se pode importar"""
    try:
        module = __import__(module_path, fromlist=[name])
        getattr(module, name)
        print(f"✅ {module_path}.{name}")
        return True
    except ImportError as e:
        print(f"❌ {module_path}.{name} - ImportError: {e}")
        return False
    except AttributeError as e:
        print(f"❌ {module_path}.{name} - AttributeError: {e}")
        return False
    except Exception as e:
        print(f"❌ {module_path}.{name} - Error: {e}")
        return False

def main():
    print("="*80)
    print("🔍 DIAGNÓSTICO DA API")
    print("="*80)
    
    all_ok = True
    
    # 1. Verificar arquivos
    print("\n📁 Verificando arquivos...")
    print("-"*80)
    files = [
        "src/__init__.py",
        "src/config.py",
        "src/pdf_extractor.py",
        "src/vectorstore.py",
        "src/rag_engine.py",
        "src/chat_interface.py",
        "api/__init__.py",
        "api/main.py",
        "api/models.py",
        "api/dependencies.py",
        "api/chat_manager.py",
        ".env"
    ]
    
    for file in files:
        if not check_file_exists(file):
            all_ok = False
    
    # 2. Verificar imports do src
    print("\n📦 Verificando imports do src...")
    print("-"*80)
    src_imports = [
        ("src.config", "load_config"),
        ("src.config", "Config"),
        ("src.vectorstore", "VectorStore"),
        ("src.rag_engine", "RAGEngine"),
        ("src.pdf_extractor", "PDFExtractor"),
    ]
    
    for module, name in src_imports:
        if not check_import(module, name):
            all_ok = False
    
    # 3. Verificar imports da API
    print("\n🌐 Verificando imports da API...")
    print("-"*80)
    api_imports = [
        ("api.models", "QueryRequest"),
        ("api.models", "QueryResponse"),
        ("api.models", "ChatRequest"),
        ("api.models", "ChatResponse"),
        ("api.dependencies", "get_rag_engine"),
        ("api.dependencies", "get_vectorstore"),
        ("api.dependencies", "get_chat_manager"),
        ("api.chat_manager", "ChatManager"),
    ]
    
    for module, name in api_imports:
        if not check_import(module, name):
            all_ok = False
    
    # 4. Verificar configuração
    print("\n⚙️  Verificando configuração...")
    print("-"*80)
    try:
        from src.config import load_config
        config = load_config()
        print(f"✅ Configuração carregada")
        print(f"   LLM: {config.llm_model}")
        print(f"   Embeddings: {config.embedding_model}")
        print(f"   Collection: {config.collection_name}")
    except Exception as e:
        print(f"❌ Erro ao carregar configuração: {e}")
        all_ok = False
    
    # 5. Verificar ChromaDB
    print("\n🗄️  Verificando ChromaDB...")
    print("-"*80)
    try:
        from src.config import load_config
        from src.vectorstore import VectorStore
        
        config = load_config()
        vs = VectorStore(config)
        stats = vs.get_collection_stats()
        
        print(f"✅ ChromaDB funcionando")
        print(f"   Total chunks: {stats.get('total_chunks', 0)}")
        print(f"   Documentos: {stats.get('unique_sources', 0)}")
        
        if stats.get('total_chunks', 0) == 0:
            print(f"⚠️  Nenhum documento indexado!")
            print(f"   Execute: python scripts/ingest_pdfs.py data/pdfs/")
    except Exception as e:
        print(f"❌ Erro no ChromaDB: {e}")
        all_ok = False
    
    # 6. Verificar dependências Python
    print("\n📚 Verificando dependências...")
    print("-"*80)
    dependencies = [
        "fastapi",
        "uvicorn",
        "pydantic",
        "langchain_openai",
        "langchain_chroma",
        "chromadb",
        "fitz",  # PyMuPDF
    ]
    
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"✅ {dep}")
        except ImportError:
            print(f"❌ {dep} - NÃO INSTALADO")
            all_ok = False
    
    # 7. Resumo
    print("\n" + "="*80)
    if all_ok:
        print("✅ TODOS OS TESTES PASSARAM")
        print("="*80)
        print("\n💡 Você pode iniciar a API com:")
        print("   uvicorn api.main:app --reload")
        print("\nOu:")
        print("   python api/main.py")
    else:
        print("❌ ALGUNS TESTES FALHARAM")
        print("="*80)
        print("\n🔧 Ações necessárias:")
        print("   1. Verifique os arquivos faltando acima")
        print("   2. Copie os artifacts corretos")
        print("   3. Instale dependências: uv pip install -r requirements_api.txt")
        print("   4. Execute novamente: python scripts/diagnose_api.py")
    
    print()
    return 0 if all_ok else 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Diagnóstico cancelado")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
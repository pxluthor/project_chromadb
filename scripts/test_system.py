#!/usr/bin/env python3
"""
Script para testar o sistema RAG
"""
import sys
from pathlib import Path

# Adiciona o diretório src ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import load_config
from src.pdf_extractor import PDFExtractor
from src.vectorstore import VectorStore
from src.rag_engine import RAGEngine


def test_configuration():
    """Testa carregamento de configuração"""
    print("\n" + "="*80)
    print("🧪 Teste 1: Configuração")
    print("="*80)
    
    try:
        config = load_config()
        print("✓ Configuração carregada com sucesso")
        print(f"  LLM Model: {config.llm_model}")
        print(f"  Embedding Model: {config.embedding_model}")
        print(f"  Chunk Size: {config.chunk_size}")
        print(f"  Collection: {config.collection_name}")
        print(f"  PDFs Directory: {config.pdfs_dir}")
        print(f"  ChromaDB Directory: {config.chroma_dir}")
        return True
    except Exception as e:
        print(f"❌ Erro ao carregar configuração: {e}")
        return False


def test_openai_connection():
    """Testa conexão com OpenAI"""
    print("\n" + "="*80)
    print("🧪 Teste 2: Conexão OpenAI")
    print("="*80)
    
    try:
        from openai import OpenAI
        config = load_config()
        
        client = OpenAI(api_key=config.openai_api_key)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Diga 'OK' se você está funcionando."}],
            max_tokens=10
        )
        
        print("✓ Conexão com OpenAI estabelecida")
        print(f"  Resposta: {response.choices[0].message.content}")
        return True
    except Exception as e:
        print(f"❌ Erro ao conectar com OpenAI: {e}")
        return False


def test_pdf_extraction():
    """Testa extração de PDF"""
    print("\n" + "="*80)
    print("🧪 Teste 3: Extração de PDF")
    print("="*80)
    
    try:
        config = load_config()
        extractor = PDFExtractor()
        
        # Verifica se há PDFs no diretório
        pdf_files = list(config.pdfs_dir.glob("*.pdf"))
        
        if not pdf_files:
            print("⚠️  Nenhum PDF encontrado no diretório de PDFs")
            print(f"   Adicione arquivos PDF em: {config.pdfs_dir}")
            return False
        
        # Testa extração do primeiro PDF
        test_pdf = pdf_files[0]
        print(f"  Testando: {test_pdf.name}")
        
        doc = extractor.extract_from_file(test_pdf)
        
        print(f"✓ PDF extraído com sucesso")
        print(f"  Título: {doc.metadata['title']}")
        print(f"  Páginas: {doc.total_pages}")
        print(f"  Caracteres: {doc.total_characters:,}")
        return True
        
    except Exception as e:
        print(f"❌ Erro na extração de PDF: {e}")
        return False


def test_vectorstore():
    """Testa VectorStore"""
    print("\n" + "="*80)
    print("🧪 Teste 4: VectorStore")
    print("="*80)
    
    try:
        config = load_config()
        vectorstore = VectorStore(config)
        
        # Verifica estatísticas
        stats = vectorstore.get_collection_stats()
        
        if stats.get("total_chunks", 0) == 0:
            print("⚠️  VectorStore está vazio")
            print("   Execute 'python scripts/ingest_pdfs.py <caminho>' primeiro")
            return False
        
        print("✓ VectorStore inicializado")
        print(f"  Total de chunks: {stats['total_chunks']}")
        print(f"  Documentos únicos: {stats['unique_sources']}")
        print(f"  Collection: {stats['collection_name']}")
        
        # Testa busca
        test_query = "teste"
        results = vectorstore.search(test_query, k=1)
        print(f"\n  Teste de busca (query='{test_query}'):")
        print(f"  ✓ Retornou {len(results)} resultado(s)")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no VectorStore: {e}")
        return False


def test_rag_engine():
    """Testa RAG Engine"""
    print("\n" + "="*80)
    print("🧪 Teste 5: RAG Engine")
    print("="*80)
    
    try:
        config = load_config()
        vectorstore = VectorStore(config)
        
        # Verifica se há dados
        stats = vectorstore.get_collection_stats()
        if stats.get("total_chunks", 0) == 0:
            print("⚠️  VectorStore está vazio")
            print("   Execute 'python scripts/ingest_pdfs.py <caminho>' primeiro")
            return False
        
        rag_engine = RAGEngine(config, vectorstore)
        
        # Testa query simples
        test_question = "Qual é o tema principal dos documentos?"
        print(f"  Pergunta de teste: {test_question}")
        
        result = rag_engine.query(test_question, k=3, include_sources=True)
        
        print(f"\n✓ RAG Engine funcionando")
        print(f"  Pergunta: {result['question']}")
        print(f"  Fontes consultadas: {result['num_sources']}")
        print(f"\n  Resposta:")
        print(f"  {result['answer'][:200]}...")
        
        if result.get('sources'):
            print(f"\n  Fontes:")
            for i, source in enumerate(result['sources'][:2], 1):
                print(f"    {i}. {source['source']} - Página {source['page']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no RAG Engine: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_chat_interface():
    """Testa interface de chat"""
    print("\n" + "="*80)
    print("🧪 Teste 6: Chat Interface")
    print("="*80)
    
    try:
        config = load_config()
        vectorstore = VectorStore(config)
        
        # Verifica se há dados
        stats = vectorstore.get_collection_stats()
        if stats.get("total_chunks", 0) == 0:
            print("⚠️  VectorStore está vazio")
            return False
        
        from src.chat_interface import ChatInterface
        
        rag_engine = RAGEngine(config, vectorstore)
        chat = ChatInterface(config, vectorstore, rag_engine)
        
        # Testa mensagem
        response = chat.send_message("Olá, você pode me ajudar?")
        
        print("✓ Chat Interface funcionando")
        print(f"  Mensagens no histórico: {len(chat.chat_history)}")
        print(f"\n  Resposta:")
        print(f"  {response['answer'][:200]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no Chat Interface: {e}")
        return False


def main():
    """Executa todos os testes"""
    print("\n" + "="*80)
    print("🚀 TESTES DO SISTEMA PDF RAG")
    print("="*80)
    
    tests = [
        ("Configuração", test_configuration),
        ("Conexão OpenAI", test_openai_connection),
        ("Extração de PDF", test_pdf_extraction),
        ("VectorStore", test_vectorstore),
        ("RAG Engine", test_rag_engine),
        ("Chat Interface", test_chat_interface)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"\n❌ Erro crítico no teste '{test_name}': {e}")
            results.append((test_name, False))
    
    # Resumo
    print("\n" + "="*80)
    print("📊 RESUMO DOS TESTES")
    print("="*80)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASSOU" if success else "❌ FALHOU"
        print(f"  {status} - {test_name}")
    
    print(f"\n{'='*80}")
    print(f"Resultado: {passed}/{total} testes passaram")
    print(f"{'='*80}")
    
    if passed == total:
        print("\n🎉 Todos os testes passaram! Sistema funcionando corretamente.")
        sys.exit(0)
    else:
        print("\n⚠️  Alguns testes falharam. Verifique os erros acima.")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Testes cancelados pelo usuário")
        sys.exit(1)
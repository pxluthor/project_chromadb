#!/usr/bin/env python3
"""
Interface de chat conversacional CLI
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.config import load_config
from src.vectorstore import VectorStore
from src.rag_engine import RAGEngine
from src.chat_interface import ChatInterface


def print_banner():
    """Imprime banner do chat"""
    print("\n" + "="*80)
    print("💬 CHAT CONVERSACIONAL - PDF RAG SYSTEM")
    print("="*80)
    print("Converse com seus documentos de forma natural!")
    print("\nComandos disponíveis:")
    print("  /help     - Mostra esta ajuda")
    print("  /stats    - Mostra estatísticas do sistema")
    print("  /history  - Mostra histórico da conversa")
    print("  /clear    - Limpa o histórico")
    print("  /export   - Exporta a conversa")
    print("  /quit     - Sai do chat")
    print("="*80 + "\n")


def print_help():
    """Imprime ajuda"""
    print("\n📚 AJUDA")
    print("─"*80)
    print("Este é um assistente baseado em RAG (Retrieval-Augmented Generation).")
    print("Ele responde perguntas baseando-se nos documentos PDF indexados.\n")
    print("Comandos:")
    print("  /help     - Mostra esta ajuda")
    print("  /stats    - Estatísticas dos documentos indexados")
    print("  /history  - Mostra todo o histórico da conversa")
    print("  /clear    - Limpa o histórico (começa conversa nova)")
    print("  /export   - Exporta conversa para arquivo JSON")
    print("  /quit     - Sai do programa")
    print("\nDicas:")
    print("  • Faça perguntas específicas sobre o conteúdo dos documentos")
    print("  • O assistente cita as fontes quando possível")
    print("  • Use o histórico para fazer perguntas de acompanhamento")
    print("─"*80 + "\n")


def print_stats(chat: ChatInterface):
    """Imprime estatísticas"""
    print("\n📊 ESTATÍSTICAS")
    print("─"*80)
    
    # Estatísticas da collection
    vs_stats = chat.vectorstore.get_collection_stats()
    print(f"📚 Banco de Documentos:")
    print(f"  Total de chunks: {vs_stats.get('total_chunks', 0):,}")
    print(f"  Documentos únicos: {vs_stats.get('unique_sources', 0)}")
    print(f"  Collection: {vs_stats.get('collection_name', 'N/A')}")
    
    if vs_stats.get('sources'):
        print(f"\n  Documentos indexados:")
        for source in vs_stats['sources']:
            print(f"    • {source}")
    
    # Estatísticas da sessão
    session = chat.get_session_info()
    print(f"\n💬 Sessão Atual:")
    print(f"  Duração: {session['duration_seconds']} segundos")
    print(f"  Mensagens: {session['total_messages']} "
          f"({session['user_messages']} suas, {session['assistant_messages']} do assistente)")
    
    print("─"*80 + "\n")


def handle_command(command: str, chat: ChatInterface) -> bool:
    """
    Processa comandos especiais
    
    Returns:
        True se deve continuar, False se deve sair
    """
    command = command.lower().strip()
    
    if command == "/quit" or command == "/exit":
        print("\n👋 Até logo!\n")
        return False
    
    elif command == "/help":
        print_help()
    
    elif command == "/stats":
        print_stats(chat)
    
    elif command == "/history":
        print("\n" + chat.format_conversation() + "\n")
    
    elif command == "/clear":
        chat.clear_history()
        print("\n🗑️  Histórico limpo. Nova conversa iniciada.\n")
    
    elif command == "/export":
        from datetime import datetime
        filename = f"chat_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        chat.export_conversation(filename)
    
    else:
        print(f"\n❌ Comando desconhecido: {command}")
        print("   Use /help para ver os comandos disponíveis\n")
    
    return True


def main():
    """Função principal do chat"""
    try:
        # Carrega configuração
        config = load_config()
        
        # Inicializa componentes
        vectorstore = VectorStore(config)
        
        # Verifica se há documentos indexados
        stats = vectorstore.get_collection_stats()
        if stats.get("total_chunks", 0) == 0:
            print("\n❌ Erro: Nenhum documento indexado!")
            print("   Execute primeiro: python scripts/ingest_pdfs.py <caminho>\n")
            sys.exit(1)
        
        rag_engine = RAGEngine(config, vectorstore)
        chat = ChatInterface(config, vectorstore, rag_engine)
        
        # Banner
        print_banner()
        
        # Info inicial
        print(f"✓ Sistema carregado com sucesso!")
        print(f"  Modelo: {config.llm_model}")
        print(f"  Documentos indexados: {stats.get('unique_sources', 0)}")
        print(f"  Total de chunks: {stats.get('total_chunks', 0):,}")
        print("\nDigite sua pergunta ou /help para ajuda\n")
        
        # Loop principal
        while True:
            try:
                # Input do usuário
                user_input = input("👤 Você: ").strip()
                
                if not user_input:
                    continue
                
                # Processa comandos
                if user_input.startswith("/"):
                    if not handle_command(user_input, chat):
                        break
                    continue
                
                # Envia mensagem
                print("\n🤖 Assistente: ", end="", flush=True)
                
                response = chat.send_message(user_input)
                
                # Imprime resposta
                print(response["answer"])
                
                # Mostra fontes se houver
                if response.get("sources") and response["num_sources"] > 0:
                    print(f"\n📚 Fontes consultadas ({response['num_sources']} chunks):")
                    for i, source in enumerate(response["sources"][:3], 1):
                        print(f"  [{i}] {source['source']} - Página {source['page']}")
                
                print()  # Linha em branco
                
            except KeyboardInterrupt:
                print("\n\n⚠️  Use /quit para sair ou continue digitando...\n")
                continue
            
            except Exception as e:
                print(f"\n❌ Erro ao processar mensagem: {e}\n")
                continue
    
    except KeyboardInterrupt:
        print("\n\n👋 Até logo!\n")
        sys.exit(0)
    
    except Exception as e:
        print(f"\n❌ Erro fatal: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
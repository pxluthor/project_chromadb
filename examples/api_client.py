"""
Cliente exemplo para consumir a API PDF RAG

Demonstra como um agente de IA pode usar a API
"""
import requests
from typing import Dict, List, Optional
import json


class PDFRAGClient:
    """Cliente para a API PDF RAG"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Inicializa o cliente
        
        Args:
            base_url: URL base da API
        """
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
    
    def health_check(self) -> Dict:
        """Verifica status da API"""
        response = self.session.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()
    
    def get_stats(self) -> Dict:
        """Obtém estatísticas do banco vetorial"""
        response = self.session.get(f"{self.base_url}/stats")
        response.raise_for_status()
        return response.json()
    
    def query(
        self,
        question: str,
        k: int = 6,
        include_sources: bool = True
    ) -> Dict:
        """
        Faz uma pergunta e recebe resposta
        
        Args:
            question: Pergunta a ser respondida
            k: Número de chunks a recuperar
            include_sources: Incluir fontes na resposta
            
        Returns:
            Resposta com answer e sources
        """
        payload = {
            "question": question,
            "k": k,
            "include_sources": include_sources
        }
        
        response = self.session.post(
            f"{self.base_url}/query",
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    def search(
        self,
        query: str,
        k: int = 5,
        filter_dict: Optional[Dict] = None
    ) -> Dict:
        """
        Busca chunks similares
        
        Args:
            query: Texto de busca
            k: Número de resultados
            filter_dict: Filtros opcionais
            
        Returns:
            Lista de chunks relevantes
        """
        payload = {
            "query": query,
            "k": k
        }
        
        if filter_dict:
            payload["filter"] = filter_dict
        
        response = self.session.post(
            f"{self.base_url}/search",
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    def chat(
        self,
        session_id: str,
        message: str,
        k: int = 6
    ) -> Dict:
        """
        Envia mensagem em chat conversacional
        
        Args:
            session_id: ID da sessão
            message: Mensagem do usuário
            k: Número de chunks
            
        Returns:
            Resposta do assistente
        """
        payload = {
            "session_id": session_id,
            "message": message,
            "k": k
        }
        
        response = self.session.post(
            f"{self.base_url}/chat",
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    def get_chat_history(self, session_id: str) -> Dict:
        """Obtém histórico de uma sessão"""
        response = self.session.get(
            f"{self.base_url}/chat/{session_id}/history"
        )
        response.raise_for_status()
        return response.json()
    
    def clear_chat_session(self, session_id: str) -> Dict:
        """Limpa histórico de uma sessão"""
        response = self.session.delete(
            f"{self.base_url}/chat/{session_id}"
        )
        response.raise_for_status()
        return response.json()


# ============================================================================
# EXEMPLOS DE USO
# ============================================================================

def example_basic_query():
    """Exemplo: Query simples"""
    print("\n" + "="*80)
    print("EXEMPLO 1: Query Simples")
    print("="*80)
    
    client = PDFRAGClient()
    
    # Faz uma pergunta
    result = client.query(
        question="Qual é o tema principal dos documentos?",
        k=6,
        include_sources=True
    )
    
    print(f"\nPergunta: {result['question']}")
    print(f"\nResposta:\n{result['answer']}")
    
    if result['sources']:
        print(f"\n📚 Fontes ({result['num_sources']}):")
        for i, source in enumerate(result['sources'][:3], 1):
            print(f"  [{i}] {source['source']} - Página {source['page']}")


def example_search_chunks():
    """Exemplo: Busca de chunks"""
    print("\n" + "="*80)
    print("EXEMPLO 2: Busca de Chunks")
    print("="*80)
    
    client = PDFRAGClient()
    
    # Busca chunks sobre um tópico
    result = client.search(
        query="inteligência artificial",
        k=5
    )
    
    print(f"\nQuery: {result['query']}")
    print(f"Total de resultados: {result['total_results']}\n")
    
    for i, chunk in enumerate(result['chunks'], 1):
        print(f"[{i}] {chunk['metadata']['source']} - Página {chunk['metadata']['page']}")
        print(f"    {chunk['content'][:150]}...\n")


def example_conversational_chat():
    """Exemplo: Chat conversacional"""
    print("\n" + "="*80)
    print("EXEMPLO 3: Chat Conversacional")
    print("="*80)
    
    client = PDFRAGClient()
    session_id = "user-123"
    
    # Primeira mensagem
    response1 = client.chat(
        session_id=session_id,
        message="O que são redes neurais?"
    )
    
    print(f"\n👤 Usuário: O que são redes neurais?")
    print(f"🤖 Assistente: {response1['response'][:200]}...")
    
    # Pergunta de follow-up
    response2 = client.chat(
        session_id=session_id,
        message="Como elas funcionam?"
    )
    
    print(f"\n👤 Usuário: Como elas funcionam?")
    print(f"🤖 Assistente: {response2['response'][:200]}...")
    
    # Ver histórico
    history = client.get_chat_history(session_id)
    print(f"\n📜 Total de mensagens no histórico: {history['total_messages']}")


def example_agent_workflow():
    """Exemplo: Workflow de um agente de IA"""
    print("\n" + "="*80)
    print("EXEMPLO 4: Workflow de Agente de IA")
    print("="*80)
    
    client = PDFRAGClient()
    
    # Simula um agente respondendo a um cliente
    customer_question = "Como posso melhorar o desempenho do modelo?"
    
    print(f"\n🙋 Cliente: {customer_question}")
    
    # Passo 1: Buscar contexto relevante
    print("\n[Agente] Buscando informações relevantes...")
    search_result = client.search(
        query=customer_question,
        k=5
    )
    
    print(f"[Agente] Encontrados {search_result['total_results']} chunks relevantes")
    
    # Passo 2: Gerar resposta contextualizada
    print("[Agente] Gerando resposta...")
    query_result = client.query(
        question=customer_question,
        k=6,
        include_sources=True
    )
    
    print(f"\n🤖 Agente responde:\n{query_result['answer']}")
    
    # Passo 3: Citar fontes
    if query_result['sources']:
        print(f"\n📚 Baseado em:")
        for source in query_result['sources'][:2]:
            print(f"  • {source['source']}, página {source['page']}")


def example_with_filters():
    """Exemplo: Busca com filtros"""
    print("\n" + "="*80)
    print("EXEMPLO 5: Busca com Filtros")
    print("="*80)
    
    client = PDFRAGClient()
    
    # Buscar apenas em um documento específico
    result = client.search(
        query="machine learning",
        k=3,
        filter_dict={"source": "manual.pdf"}
    )
    
    print(f"\nBuscando 'machine learning' apenas em 'manual.pdf'")
    print(f"Resultados encontrados: {result['total_results']}\n")
    
    for chunk in result['chunks']:
        print(f"  - Página {chunk['metadata']['page']}")
        print(f"    {chunk['content'][:100]}...\n")


def example_health_and_stats():
    """Exemplo: Health check e estatísticas"""
    print("\n" + "="*80)
    print("EXEMPLO 6: Health Check e Estatísticas")
    print("="*80)
    
    client = PDFRAGClient()
    
    # Health check
    health = client.health_check()
    print("\n✓ Status da API:", health['status'])
    print("  Componentes:", health['components'])
    print("  Total de chunks:", health['total_documents'])
    
    # Estatísticas
    stats = client.get_stats()
    print(f"\n📊 Estatísticas:")
    print(f"  Total de chunks: {stats['total_chunks']}")
    print(f"  Documentos únicos: {stats['unique_sources']}")
    print(f"  Collection: {stats['collection_name']}")
    
    if stats['sources']:
        print(f"\n  Documentos indexados:")
        for source in stats['sources']:
            print(f"    • {source}")


if __name__ == "__main__":
    try:
        # Verifica se a API está rodando
        client = PDFRAGClient()
        health = client.health_check()
        
        if health['status'] == 'healthy':
            print("✓ API está rodando e saudável!")
            
            # Executa exemplos
            example_basic_query()
            example_search_chunks()
            example_conversational_chat()
            example_agent_workflow()
            example_with_filters()
            example_health_and_stats()
            
            print("\n" + "="*80)
            print("✅ Todos os exemplos executados com sucesso!")
            print("="*80 + "\n")
        else:
            print("⚠️  API está rodando mas não está saudável")
            
    except requests.exceptions.ConnectionError:
        print("\n❌ Erro: Não foi possível conectar à API")
        print("   Certifique-se de que a API está rodando:")
        print("   python api/main.py")
        print("\n   Ou:")
        print("   uvicorn api.main:app --reload\n")
    except Exception as e:
        print(f"\n❌ Erro: {e}\n")
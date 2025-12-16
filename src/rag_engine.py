"""
Engine RAG principal para geração de respostas com suporte a multimídia
"""
from typing import List, Dict, Optional
from langchain_openai import ChatOpenAI
from langchain_core.documents import Document

from .config import Config
from .vectorstore import VectorStore
from .multimedia_manager import MultimediaManager
from urllib.parse import quote


class RAGEngine:
    """Engine RAG para responder perguntas baseado em documentos com suporte a multimídia"""
    
    def __init__(
        self, 
        config: Config, 
        vectorstore: VectorStore,
        enable_multimedia: bool = True
    ):
        """
        Inicializa o RAG Engine
        
        Args:
            config: Configuração do sistema
            vectorstore: Instância do VectorStore
            enable_multimedia: Ativar suporte a multimídia
        """
        self.config = config
        self.vectorstore = vectorstore
        self.enable_multimedia = enable_multimedia
        
        # Inicializa o LLM
        self.llm = ChatOpenAI(
            model=config.llm_model,
            temperature=config.temperature,
            openai_api_key=config.openai_api_key
        )
        
        # Inicializa gerenciador de multimídia
        if self.enable_multimedia:
            try:
                self.multimedia_manager = MultimediaManager()
                print(f"✓ Multimídia ativada: {self.multimedia_manager.get_statistics()['total_media_items']} itens")
            except Exception as e:
                print(f"⚠️  Erro ao carregar multimídia: {e}")
                self.enable_multimedia = False
                self.multimedia_manager = None
        else:
            self.multimedia_manager = None
    
    def query(
        self, 
        question: str, 
        k: Optional[int] = None,
        include_sources: bool = True,
        include_media: bool = True
    ) -> Dict[str, any]:
        """
        Faz uma pergunta e retorna resposta baseada nos documentos
        """
        # Busca contexto relevante
        relevant_docs = self.vectorstore.search(question, k=k)
        
        if not relevant_docs:
            return {
                "question": question,
                "answer": "Desculpe, não encontrei informações relevantes.",
                "sources": [],
                "num_sources": 0,
                "media": [],
                "has_media": False
            }
        
        # Gera resposta
        answer = self._generate_answer(question, relevant_docs)
        
        result = {
            "question": question,
            "answer": answer,
            "num_sources": len(relevant_docs),
            "media": [],        
            "has_media": False
        }
        
        if include_sources:
            sources = self._format_sources(relevant_docs)
            
            if include_media and self.enable_multimedia and self.multimedia_manager:
                # 1. Enriquece as fontes
                sources = self.multimedia_manager.enrich_sources_with_media(
                    sources,
                    query=question
                )
                
                # 2. Agregação BLINDADA (Copia das fontes para a raiz)
                all_media = []
                seen_urls = set()
                
                for source in sources:
                    # Garante que pegamos a lista, mesmo que seja None
                    media_list = source.get('media') or []
                    
                    for item in media_list:
                        # --- NORMALIZAÇÃO DE DADOS ---
                        # Se o item já virou um objeto Pydantic ou Dataclass, converte para dict
                        item_dict = item
                        if hasattr(item, "model_dump"): # Pydantic v2
                            item_dict = item.model_dump()
                        elif hasattr(item, "dict"): # Pydantic v1
                            item_dict = item.dict()
                        elif hasattr(item, "to_dict"): # Nossa classe MediaItem
                            item_dict = item.to_dict()
                        
                        # Agora garantimos que é um dicionário
                        if isinstance(item_dict, dict):
                            url = item_dict.get('url')
                            
                            # Validação simples e permissiva
                            if url and isinstance(url, str) and len(url.strip()) > 1:
                                if url not in seen_urls:
                                    all_media.append(item_dict)
                                    seen_urls.add(url)

                # 3. Busca por keywords (Fallback)
                if not all_media:
                     keyword_results = self.multimedia_manager.find_media_by_keywords(question, top_k=2)
                     for res in keyword_results:
                         for item in res['media_items']:
                             item_dict = item.to_dict()
                             url = item_dict.get('url')
                             if url and len(str(url)) > 1 and url not in seen_urls:
                                 all_media.append(item_dict)
                                 seen_urls.add(url)

                result["media"] = all_media
                result["has_media"] = len(all_media) > 0
            
            result["sources"] = sources
            
        return result

    def query_old(  # não está trazendo a mídia para a raiz
        self, 
        question: str, 
        k: Optional[int] = None,
        include_sources: bool = True,
        include_media: bool = True
    ) -> Dict[str, any]:
        """
        Faz uma pergunta e retorna resposta baseada nos documentos
        
        Args:
            question: Pergunta do usuário
            k: Número de chunks a recuperar
            include_sources: Se True, inclui documentos fonte
            include_media: Se True, inclui mídia associada (imagens/vídeos)
            
        Returns:
            Dicionário com resposta e metadados
        """
        # Busca contexto relevante
        relevant_docs = self.vectorstore.search(question, k=k)
        
        if not relevant_docs:
            return {
                "question": question,
                "answer": "Desculpe, não encontrei informações relevantes nos documentos para responder sua pergunta.",
                "sources": [],
                "num_sources": 0,
                "media": []
            }
        
        # Gera resposta
        answer = self._generate_answer(question, relevant_docs)
        
        result = {
            "question": question,
            "answer": answer,
            "num_sources": len(relevant_docs),
            "media": [],        
            "has_media": False  
        }
        
        # Adiciona fontes se solicitado
        if include_sources:
            sources = self._format_sources(relevant_docs)
            
            # Enriquece com multimídia se ativado
            if include_media and self.enable_multimedia and self.multimedia_manager:
                sources = self.multimedia_manager.enrich_sources_with_media(
                    sources,
                    query=question
                )
                all_media = []
                seen_urls = set()
                
                for source in sources:
                    if 'media' in source:
                        for item in source['media']:
                            # Evita duplicatas (ex: mesma imagem em 2 chunks da mesma página)
                            if item['url'] not in seen_urls:
                                all_media.append(item)
                                seen_urls.add(item['url'])
                
                # Se não achou nada por página, tenta uma busca geral por keywords nas mídias
                if not all_media:
                     keyword_results = self.multimedia_manager.find_media_by_keywords(question, top_k=2)
                     for res in keyword_results:
                         for item in res['media_items']:
                             if item.url not in seen_urls:
                                 all_media.append(item.to_dict()) # to_dict pois vem do objeto
                                 seen_urls.add(item.url)

                result["sources"] = sources
                result["media"] = all_media
                result["has_media"] = len(all_media) > 0
                
        return result
    
        #     result["sources"] = sources
            
        #     # Extrai mídia de todas as fontes para fácil acesso
        #     if include_media:
        #         all_media = []
        #         for source in sources:
        #             if 'media' in source:
        #                 all_media.extend(source['media'])
                
        #         result["media"] = all_media
        #         result["has_media"] = len(all_media) > 0
        
        # return result
    
    def _generate_answer(self, question: str, context_docs: List[Document]) -> str:
        """
        Gera resposta usando LLM com contexto
        
        Args:
            question: Pergunta do usuário
            context_docs: Documentos de contexto
            
        Returns:
            Resposta gerada
        """
        # Formata o contexto
        context_text = self._format_context(context_docs)
        
        # Cria o prompt
        prompt = self._build_prompt(question, context_text)
        
        # Invoca o LLM
        response = self.llm.invoke(prompt)
        return response.content
    
    def _format_context(self, docs: List[Document]) -> str:
        """Formata documentos em contexto para o prompt"""
        formatted_chunks = []
        
        for i, doc in enumerate(docs, 1):
            source = doc.metadata.get("source", "Desconhecido")
            page = doc.metadata.get("page", "N/A")
            
            chunk = f"[Documento {i} - {source}, Página {page}]\n{doc.page_content}"
            formatted_chunks.append(chunk)
        
        return "\n\n---\n\n".join(formatted_chunks)
    
    def _build_prompt(self, question: str, context: str) -> str:
        """Constrói o prompt para o LLM"""
        return f"""Você é um assistente especializado em análise de documentos PDF. 
Sua função é responder perguntas baseando-se EXCLUSIVAMENTE no contexto fornecido abaixo.

INSTRUÇÕES IMPORTANTES:
1. Use APENAS as informações presentes no contexto fornecido
2. Se a informação não estiver no contexto, diga claramente que não encontrou
3. Cite as fontes (documento e página) quando relevante
4. Seja preciso, claro e objetivo
5. Organize a resposta de forma estruturada quando apropriado
6. Se houver informações conflitantes, mencione isso

CONTEXTO DOS DOCUMENTOS:
{context}

PERGUNTA DO USUÁRIO: {question}

RESPOSTA:"""
    
    def _format_sources(self, docs: List[Document]) -> List[Dict[str, any]]:
        """Formata documentos fonte para resposta"""
        sources = []

        base_url = "http://10.1.254.180:8005/pdfs"

        for doc in docs:
            filename = doc.metadata.get("source", "Desconhecido")
            safe_filename = quote(filename)
            pdf_url = f"{base_url}/{safe_filename}"

            source_info = {
                "source": doc.metadata.get("source", "Desconhecido"),
                "page": doc.metadata.get("page", "N/A"),
                "title": doc.metadata.get("title", "Sem título"),
                "excerpt": doc.page_content[:300] + "..." if len(doc.page_content) > 300 else doc.page_content,
                "pdf_url": pdf_url
            }
            sources.append(source_info)
        
        return sources
    
    def chat_query(
        self,
        question: str,
        chat_history: List[Dict[str, str]],
        k: Optional[int] = None,
        include_media: bool = True
    ) -> Dict[str, any]:
        """
        Pergunta com histórico de conversa
        
        Args:
            question: Pergunta atual
            chat_history: Histórico de mensagens
            k: Número de chunks a recuperar
            include_media: Incluir mídia associada
            
        Returns:
            Resposta com contexto da conversa
        """
        # Busca contexto relevante
        relevant_docs = self.vectorstore.search(question, k=k)
        
        if not relevant_docs:
            return {
                "question": question,
                "answer": "Desculpe, não encontrei informações relevantes nos documentos para responder sua pergunta.",
                "sources": [],
                "num_sources": 0,
                "media": []
            }
        
        # Gera resposta com histórico
        answer = self._generate_chat_answer(question, relevant_docs, chat_history)
        
        # Formata fontes
        sources = self._format_sources(relevant_docs)
        
        # Enriquece com multimídia
        if include_media and self.enable_multimedia and self.multimedia_manager:
            sources = self.multimedia_manager.enrich_sources_with_media(
                sources,
                query=question
            )
        
        # Extrai toda a mídia
        all_media = []
        for source in sources:
            if 'media' in source:
                all_media.extend(source['media'])
        
        return {
            "question": question,
            "answer": answer,
            "num_sources": len(relevant_docs),
            "sources": sources,
            "media": all_media,
            "has_media": len(all_media) > 0
        }
    
    def _generate_chat_answer(
        self,
        question: str,
        context_docs: List[Document],
        chat_history: List[Dict[str, str]]
    ) -> str:
        """Gera resposta considerando histórico de chat"""
        context_text = self._format_context(context_docs)
        
        # Formata histórico
        history_text = ""
        if chat_history:
            history_items = []
            for msg in chat_history[-6:]:  # Últimas 6 mensagens
                role = "Usuário" if msg["role"] == "user" else "Assistente"
                history_items.append(f"{role}: {msg['content']}")
            history_text = "\n".join(history_items)
        
        # Cria prompt com histórico
        prompt = f"""Você é um assistente especializado em análise de documentos PDF em uma conversa contínua.
Use o contexto dos documentos E o histórico da conversa para responder de forma natural e contextualizada.

CONTEXTO DOS DOCUMENTOS:
{context_text}

{"HISTÓRICO DA CONVERSA:" if history_text else ""}
{history_text if history_text else ""}

PERGUNTA ATUAL: {question}

INSTRUÇÕES:
1. Considere o contexto da conversa anterior
2. Use APENAS informações dos documentos fornecidos
3. Seja conversacional mas preciso
4. Cite fontes quando relevante

RESPOSTA:"""
        
        response = self.llm.invoke(prompt)
        return response.content
    
    def get_multimedia_stats(self) -> Optional[Dict]:
        """Retorna estatísticas de multimídia"""
        if self.enable_multimedia and self.multimedia_manager:
            return self.multimedia_manager.get_statistics()
        return None
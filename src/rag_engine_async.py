"""
RAG Engine Async - Versão otimizada para alta disponibilidade
Substitui src/rag_engine.py
"""
import asyncio
from typing import List, Dict, Optional
from langchain_openai import ChatOpenAI
from langchain_core.documents import Document
from concurrent.futures import ThreadPoolExecutor

from .config import Config
from .vectorstore import VectorStore
from .multimedia_manager import MultimediaManager
from urllib.parse import quote


class RAGEngineAsync:
    """Engine RAG com operações assíncronas"""
    
    def __init__(
        self, 
        config: Config, 
        vectorstore: VectorStore,
        enable_multimedia: bool = True,
        max_workers: int = 4
    ):
        self.config = config
        self.vectorstore = vectorstore
        self.enable_multimedia = enable_multimedia
        
        # Thread pool para operações síncronas
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        
        # LLM com timeout
        self.llm = ChatOpenAI(
            model=config.llm_model,
            temperature=config.temperature,
            openai_api_key=config.openai_api_key,
            timeout=30.0,  # Timeout de 30s
            max_retries=2
        )
        
        # Multimídia
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
    
    async def query(
        self, 
        question: str, 
        k: Optional[int] = None,
        include_sources: bool = True,
        include_media: bool = True
    ) -> Dict[str, any]:
        """
        Query assíncrona com paralelização
        """
        try:
            # 1. Busca vetorial em thread pool (não bloqueia)
            relevant_docs = await self._search_async(question, k)
            
            if not relevant_docs:
                return self._empty_response(question)
            
            # 2. Geração de resposta (operação mais pesada)
            answer_task = self._generate_answer_async(question, relevant_docs)
            
            # 3. Formatação de sources em paralelo
            sources_task = self._format_sources_async(relevant_docs)
            
            # Aguarda ambas as operações em paralelo
            answer, sources = await asyncio.gather(
                answer_task,
                sources_task
            )
            
            result = {
                "question": question,
                "answer": answer,
                "num_sources": len(relevant_docs),
                "media": [],
                "has_media": False
            }
            
            if include_sources:
                # 4. Enriquecimento com multimídia (se necessário)
                if include_media and self.enable_multimedia and self.multimedia_manager:
                    sources = await self._enrich_with_media_async(sources, question)
                    
                    # Agregação de mídia
                    all_media = self._aggregate_media(sources)
                    
                    # Fallback por keywords
                    if not all_media:
                        all_media = await self._find_media_by_keywords_async(question)
                    
                    result["media"] = all_media
                    result["has_media"] = len(all_media) > 0
                
                result["sources"] = sources
            
            return result
            
        except asyncio.TimeoutError:
            return {
                "question": question,
                "answer": "Desculpe, a operação excedeu o tempo limite. Tente novamente.",
                "sources": [],
                "num_sources": 0,
                "media": [],
                "has_media": False,
                "error": "timeout"
            }
        except Exception as e:
            print(f"❌ Erro na query: {e}")
            return {
                "question": question,
                "answer": f"Erro ao processar sua pergunta: {str(e)}",
                "sources": [],
                "num_sources": 0,
                "media": [],
                "has_media": False,
                "error": str(e)
            }
    
    async def _search_async(self, query: str, k: Optional[int] = None) -> List[Document]:
        """Busca vetorial assíncrona"""
        k = k or self.config.default_k
        
        # Usa método async nativo do VectorStore
        return await self.vectorstore.search_async(query, k)
    
    async def _generate_answer_async(self, question: str, context_docs: List[Document]) -> str:
        """Geração de resposta assíncrona"""
        loop = asyncio.get_event_loop()
        context_text = self._format_context(context_docs)
        prompt = self._build_prompt(question, context_text)
        
        # Executa LLM em thread pool
        def _invoke_llm():
            response = self.llm.invoke(prompt)
            return response.content
        
        return await loop.run_in_executor(self.executor, _invoke_llm)
    
    async def _format_sources_async(self, docs: List[Document]) -> List[Dict[str, any]]:
        """Formatação de sources assíncrona"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            self._format_sources_sync,
            docs
        )
    
    def _format_sources_sync(self, docs: List[Document]) -> List[Dict[str, any]]:
        """Versão síncrona da formatação"""
        sources = []
        base_url = "http://10.1.254.180:8005/pdfs"
        
        for doc in docs:
            filename = doc.metadata.get("source", "Desconhecido")
            safe_filename = quote(filename)
            pdf_url = f"{base_url}/{safe_filename}"
            origin = doc.metadata.get("_debug_origin", "Sistema (Padrão)")
            
            source_info = {
                "source": filename,
                "page": doc.metadata.get("page", "N/A"),
                "title": doc.metadata.get("title", "Sem título"),
                "excerpt": doc.page_content[:300] + "..." if len(doc.page_content) > 300 else doc.page_content,
                "pdf_url": pdf_url,
                "origin": origin
            }
            sources.append(source_info)
        
        return sources
    
    async def _enrich_with_media_async(self, sources: List[Dict], query: str) -> List[Dict]:
        """Enriquecimento com mídia assíncrono"""
        if not self.multimedia_manager:
            return sources
        
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            self.multimedia_manager.enrich_sources_with_media,
            sources,
            query
        )
    
    async def _find_media_by_keywords_async(self, query: str) -> List[Dict]:
        """Busca de mídia por keywords assíncrona"""
        if not self.multimedia_manager:
            return []
        
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(
            self.executor,
            self.multimedia_manager.find_media_by_keywords,
            query,
            2
        )
        
        all_media = []
        seen_urls = set()
        
        for res in results:
            for item in res['media_items']:
                item_dict = item.to_dict()
                url = item_dict.get('url')
                if url and len(str(url)) > 1 and url not in seen_urls:
                    all_media.append(item_dict)
                    seen_urls.add(url)
        
        return all_media
    
    def _aggregate_media(self, sources: List[Dict]) -> List[Dict]:
        """Agrega mídia de todas as sources"""
        all_media = []
        seen_urls = set()
        
        for source in sources:
            media_list = source.get('media') or []
            
            for item in media_list:
                item_dict = item
                if hasattr(item, "model_dump"):
                    item_dict = item.model_dump()
                elif hasattr(item, "dict"):
                    item_dict = item.dict()
                elif hasattr(item, "to_dict"):
                    item_dict = item.to_dict()
                
                if isinstance(item_dict, dict):
                    url = item_dict.get('url')
                    if url and isinstance(url, str) and len(url.strip()) > 1:
                        if url not in seen_urls:
                            all_media.append(item_dict)
                            seen_urls.add(url)
        
        return all_media
    
    def _format_context(self, docs: List[Document]) -> str:
        """Formata contexto (síncrono, leve)"""
        formatted_chunks = []
        
        for i, doc in enumerate(docs, 1):
            source = doc.metadata.get("source", "Desconhecido")
            page = doc.metadata.get("page", "N/A")
            chunk = f"[Documento {i} - {source}, Página {page}]\n{doc.page_content}"
            formatted_chunks.append(chunk)
        
        return "\n\n---\n\n".join(formatted_chunks)
    
    def _build_prompt(self, question: str, context: str) -> str:
        """Constrói prompt (síncrono, leve)"""
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

                    RESPOSTA:
                """
    
    def _empty_response(self, question: str) -> Dict[str, any]:
        """Resposta vazia padrão"""
        return {
            "question": question,
            "answer": "Desculpe, não encontrei informações relevantes.",
            "sources": [],
            "num_sources": 0,
            "media": [],
            "has_media": False
        }
    
    async def chat_query(
        self,
        question: str,
        chat_history: List[Dict[str, str]],
        k: Optional[int] = None,
        include_media: bool = True
    ) -> Dict[str, any]:
        """Chat com histórico (assíncrono)"""
        try:
            relevant_docs = await self._search_async(question, k)
            
            if not relevant_docs:
                return self._empty_response(question)
            
            # Gera resposta com histórico
            answer = await self._generate_chat_answer_async(question, relevant_docs, chat_history)
            
            # Formata sources
            sources = await self._format_sources_async(relevant_docs)
            
            # Mídia
            if include_media and self.enable_multimedia and self.multimedia_manager:
                sources = await self._enrich_with_media_async(sources, question)
            
            all_media = self._aggregate_media(sources)
            
            return {
                "question": question,
                "answer": answer,
                "num_sources": len(relevant_docs),
                "sources": sources,
                "media": all_media,
                "has_media": len(all_media) > 0
            }
            
        except Exception as e:
            print(f"❌ Erro no chat: {e}")
            return self._empty_response(question)
    
    async def _generate_chat_answer_async(
        self,
        question: str,
        context_docs: List[Document],
        chat_history: List[Dict[str, str]]
    ) -> str:
        """Geração de resposta com histórico (assíncrona)"""
        loop = asyncio.get_event_loop()
        
        def _generate():
            context_text = self._format_context(context_docs)
            
            history_text = ""
            if chat_history:
                history_items = []
                for msg in chat_history[-6:]:
                    role = "Usuário" if msg["role"] == "user" else "Assistente"
                    history_items.append(f"{role}: {msg['content']}")
                history_text = "\n".join(history_items)
            
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
        
        return await loop.run_in_executor(self.executor, _generate)
    
    def get_multimedia_stats(self) -> Optional[Dict]:
        """Estatísticas de multimídia"""
        if self.enable_multimedia and self.multimedia_manager:
            return self.multimedia_manager.get_statistics()
        return None
    
    async def __aenter__(self):
        """Context manager"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Cleanup"""
        self.executor.shutdown(wait=True)
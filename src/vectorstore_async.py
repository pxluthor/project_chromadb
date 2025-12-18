"""
Módulo gerenciador de Vector Stores (Factory Pattern) - VERSÃO ASYNC
Suporta: ChromaDB, Qdrant e Dual Mode (Escrita espelhada).
MANTÉM 100% da arquitetura Factory/Strategy original.
"""
import os
import asyncio
from typing import List, Dict, Optional, Any
from abc import ABC, abstractmethod
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from concurrent.futures import ThreadPoolExecutor

# Imports específicos
from langchain_chroma import Chroma
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http import models

from .pdf_extractor import PDFDocument
from .config import Config

# ==============================================================================
# 1. Interface Base - AGORA COM ASYNC
# ==============================================================================
class BaseVectorStore(ABC):
    """Interface base para Vector Stores - Agora suporta async"""
    
    def __init__(self, config: Config, max_workers: int = 4):
        self.config = config
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        
        self.embeddings = OpenAIEmbeddings(
            model=config.embedding_model,
            openai_api_key=config.openai_api_key
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.chunk_size,
            chunk_overlap=config.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )

    # ==========================================
    # MÉTODOS ASSÍNCRONOS (Para API)
    # ==========================================
    
    async def add_documents_async(self, pdf_documents: List[PDFDocument]) -> Dict[str, Any]:
        """Versão assíncrona de add_documents"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            self.add_documents,
            pdf_documents
        )
    
    async def search_async(
        self, 
        query: str, 
        k: Optional[int] = None, 
        filter_dict: Optional[Dict] = None
    ) -> List[Document]:
        """Versão assíncrona de search"""
        loop = asyncio.get_event_loop()
        
        if filter_dict:
            return await loop.run_in_executor(
                self.executor,
                self.search,
                query,
                k,
                filter_dict
            )
        else:
            return await loop.run_in_executor(
                self.executor,
                self.search,
                query,
                k,
                None
            )
    
    async def get_collection_stats_async(self) -> Dict[str, Any]:
        """Versão assíncrona de get_collection_stats"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            self.get_collection_stats
        )
    
    async def delete_document_by_name_async(self, filename: str) -> bool:
        """Versão assíncrona de delete_document_by_name"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            self.delete_document_by_name,
            filename
        )
    
    async def clear_all_data_async(self) -> None:
        """Versão assíncrona de clear_all_data"""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            self.executor,
            self.clear_all_data
        )
    
    # ==========================================
    # MÉTODOS SÍNCRONOS (Mantidos para compatibilidade)
    # ==========================================
    
    @abstractmethod
    def add_documents(self, pdf_documents: List[PDFDocument]) -> Dict[str, Any]:
        """Adiciona documentos (versão síncrona)"""
        pass

    @abstractmethod
    def search(self, query: str, k: Optional[int] = None, filter_dict: Optional[Dict] = None) -> List[Document]:
        """Busca documentos (versão síncrona)"""
        pass
    
    @abstractmethod
    def get_collection_stats(self) -> Dict[str, Any]:
        """Estatísticas (versão síncrona)"""
        pass
    
    @abstractmethod
    def delete_document_by_name(self, filename: str) -> bool:
        """Deleta documento (versão síncrona)"""
        pass
        
    @abstractmethod
    def clear_all_data(self) -> None:
        """Limpa dados (versão síncrona)"""
        pass

    def _create_chunks(self, pdf_doc: PDFDocument) -> List[Document]:
        """Helper para criar chunks (síncrono - operação leve)"""
        chunks = []
        for page in pdf_doc.pages:
            page_chunks = self.text_splitter.split_text(page.text)
            for i, chunk_text in enumerate(page_chunks):
                metadata = {
                    "source": pdf_doc.metadata["filename"],
                    "page": page.page_number,
                    "chunk_id": i,
                    "title": pdf_doc.metadata.get("title", ""),
                }
                chunks.append(Document(page_content=chunk_text, metadata=metadata))
        return chunks
    
    def __del__(self):
        """Cleanup do executor"""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=False)


# ==============================================================================
# 2. Implementação ChromaDB (Local) - HÍBRIDO
# ==============================================================================
class ChromaDBVectorStore(BaseVectorStore):
    """ChromaDB - Suporta sync e async"""
    
    def __init__(self, config: Config, max_workers: int = 4):
        super().__init__(config, max_workers)
        print(f"📂 [Chroma] Inicializando em: {config.chroma_dir}")
        self._vectorstore = Chroma(
            collection_name=config.collection_name,
            embedding_function=self.embeddings,
            persist_directory=str(config.chroma_dir)
        )
    
    # Métodos síncronos (originais)
    def add_documents(self, pdf_documents: List[PDFDocument]) -> Dict[str, Any]:
        all_chunks = []
        stats = {"total_documents": len(pdf_documents), "total_chunks": 0}
        for doc in pdf_documents:
            chunks = self._create_chunks(doc)
            all_chunks.extend(chunks)
        
        if all_chunks:
            self._vectorstore.add_documents(all_chunks)
            stats["total_chunks"] = len(all_chunks)
        return stats

    def search(self, query: str, k: Optional[int] = None, filter_dict: Optional[Dict] = None) -> List[Document]:
        k = k or self.config.default_k
        if filter_dict:
            results = self._vectorstore.similarity_search(query, k=k, filter=filter_dict)
        else:
            results = self._vectorstore.similarity_search(query, k=k)
            
        for doc in results:
            doc.metadata["_debug_origin"] = "📂 ChromaDB (Local)"
        return results

    def get_collection_stats(self) -> Dict[str, Any]:
        try:
            collection = self._vectorstore._collection
            count = collection.count()
            unique_sources = set()
            
            if count > 0:
                data = collection.get(include=["metadatas"])
                if data and "metadatas" in data:
                    for meta in data["metadatas"]:
                        if meta and "source" in meta:
                            unique_sources.add(meta["source"])

            return {
                "total_chunks": count, 
                "unique_sources": len(unique_sources),
                "sources": sorted(list(unique_sources)),
                "collection_name": self.config.collection_name, 
                "backend": "ChromaDB (Local)"
            }
        except Exception as e:
            return {"error": str(e), "backend": "ChromaDB", "sources": []}

    def delete_document_by_name(self, filename: str) -> bool:
        try:
            self._vectorstore._collection.delete(where={"source": filename})
            return True
        except:
            return False

    def clear_all_data(self) -> None:
        try:
            self._vectorstore.delete_collection()
        except:
            pass


# ==============================================================================
# 3. Implementação Qdrant (Remoto) - HÍBRIDO
# ==============================================================================
class QdrantVectorStoreImp(BaseVectorStore):
    """Qdrant - Suporta sync e async"""
    
    def __init__(self, config: Config, max_workers: int = 4):
        super().__init__(config, max_workers)
        print(f"🔌 [Qdrant] Conectando a: {config.qdrant_host}:{config.qdrant_port}")
        
        self.client = QdrantClient(
            url=config.qdrant_host,
            port=config.qdrant_port,
            api_key=config.qdrant_api_key,
            check_compatibility=False
        )
        
        if not self.client.collection_exists(config.collection_name):
            self.client.create_collection(
                collection_name=config.collection_name,
                vectors_config=models.VectorParams(size=1536, distance=models.Distance.COSINE)
            )

        self._vectorstore = QdrantVectorStore(
            client=self.client,
            collection_name=config.collection_name,
            embedding=self.embeddings,
        )

    # Métodos síncronos (originais)
    def add_documents(self, pdf_documents: List[PDFDocument]) -> Dict[str, Any]:
        all_chunks = []
        stats = {"total_documents": len(pdf_documents), "total_chunks": 0}
        for doc in pdf_documents:
            chunks = self._create_chunks(doc)
            all_chunks.extend(chunks)
        
        if all_chunks:
            self._vectorstore.add_documents(all_chunks, batch_size=100)
            stats["total_chunks"] = len(all_chunks)
        return stats

    def search(self, query: str, k: Optional[int] = None, filter_dict: Optional[Dict] = None) -> List[Document]:
        k = k or self.config.default_k
        results = self._vectorstore.similarity_search(query, k=k, filter=filter_dict)
        
        for doc in results:
            doc.metadata["_debug_origin"] = "🚀 Qdrant (Server)"
        return results

    def get_collection_stats(self) -> Dict[str, Any]:
        try:
            collection_name = self.config.collection_name
            if not self.client.collection_exists(collection_name):
                 return {"total_chunks": 0, "unique_sources": 0, "sources": [], "backend": "Qdrant"}

            info = self.client.get_collection(collection_name)
            count = info.points_count
            unique_sources = set()

            if count > 0:
                limit_scan = 5000 
                scroll_result, _ = self.client.scroll(
                    collection_name=collection_name,
                    limit=min(count, limit_scan),
                    with_payload=True,
                    with_vectors=False
                )
                for point in scroll_result:
                    if point.payload:
                        src = point.payload.get("source")
                        if not src and "metadata" in point.payload:
                            if isinstance(point.payload["metadata"], dict):
                                src = point.payload["metadata"].get("source")
                        if not src:
                             src = point.payload.get("filename")
                             
                        if src:
                            unique_sources.add(src)

            return {
                "total_chunks": count, 
                "unique_sources": len(unique_sources),
                "sources": sorted(list(unique_sources)),
                "collection_name": collection_name, 
                "backend": "Qdrant (Server)"
            }
        except Exception as e:
            print(f"Erro Qdrant Stats: {e}")
            return {"error": str(e), "backend": "Qdrant", "sources": []}

    def delete_document_by_name(self, filename: str) -> bool:
        try:
            self.client.delete(
                collection_name=self.config.collection_name,
                points_selector=models.FilterSelector(
                    filter=models.Filter(
                        should=[
                            models.FieldCondition(key="source", match=models.MatchValue(value=filename)),
                            models.FieldCondition(key="metadata.source", match=models.MatchValue(value=filename))
                        ]
                    )
                )
            )
            return True
        except Exception as e:
            print(f"Erro ao deletar no Qdrant: {e}")
            return False

    def clear_all_data(self) -> None:
        try:
            self.client.delete_collection(self.config.collection_name)
        except:
            pass


# ==============================================================================
# 4. Implementação DUAL (Híbrida) - HÍBRIDO
# ==============================================================================
class DualVectorStore(BaseVectorStore):
    """Gerencia Chroma e Qdrant - Suporta sync e async"""
    
    def __init__(self, config: Config, max_workers: int = 4):
        super().__init__(config, max_workers)
        print("\n🚀 [DUAL MODE] Inicializando Sistema Híbrido (Chroma + Qdrant)")
        
        self.chroma = ChromaDBVectorStore(config, max_workers)
        
        try:
            self.qdrant = QdrantVectorStoreImp(config, max_workers)
            self._qdrant_online = True
        except Exception as e:
            print(f"⚠️ AVISO: Qdrant offline ({e}). Operando apenas com Chroma.")
            self._qdrant_online = False
            self.qdrant = None

    # Métodos síncronos (originais)
    def add_documents(self, pdf_documents: List[PDFDocument]) -> Dict[str, Any]:
        stats = {"backend": "Dual", "details": []}
        
        try:
            print(">> [Dual] Gravando no Chroma...")
            chroma_stats = self.chroma.add_documents(pdf_documents)
            stats["chroma"] = "OK"
            stats["total_chunks"] = chroma_stats.get("total_chunks", 0)
        except Exception as e:
            print(f"❌ Erro Chroma: {e}")
            stats["chroma"] = str(e)

        if self._qdrant_online:
            try:
                print(">> [Dual] Gravando no Qdrant...")
                qdrant_stats = self.qdrant.add_documents(pdf_documents)
                stats["qdrant"] = "OK"
                stats["total_chunks"] = qdrant_stats.get("total_chunks", stats.get("total_chunks"))
            except Exception as e:
                print(f"❌ Erro Qdrant: {e}")
                stats["qdrant"] = str(e)
        else:
            stats["qdrant"] = "Offline"

        return stats

    def search(self, query: str, k: Optional[int] = None, filter_dict: Optional[Dict] = None) -> List[Document]:
        if self._qdrant_online:
            try:
                return self.qdrant.search(query, k, filter_dict)
            except Exception as e:
                print(f"⚠️ [FALLBACK] Erro no Qdrant: {e}. Usando Chroma.")

        print(">> [Dual] Buscando no ChromaDB")
        return self.chroma.search(query, k, filter_dict)

    def get_collection_stats(self) -> Dict[str, Any]:
        chroma_stats = {"status": "error", "total_chunks": 0, "sources": []}
        try:
            chroma_stats = self.chroma.get_collection_stats()
            chroma_stats["status"] = "online"
        except Exception as e:
            chroma_stats["error"] = str(e)

        qdrant_stats = {"status": "offline", "total_chunks": 0, "sources": []}
        if self._qdrant_online:
            try:
                qdrant_stats = self.qdrant.get_collection_stats()
                qdrant_stats["status"] = "online"
            except Exception as e:
                qdrant_stats["status"] = "error"
                qdrant_stats["error"] = str(e)

        c_sources = set(chroma_stats.get("sources", []))
        q_sources = set(qdrant_stats.get("sources", []))
        all_sources = sorted(list(c_sources | q_sources))
        
        total_chunks = max(chroma_stats.get("total_chunks", 0), qdrant_stats.get("total_chunks", 0))

        backend_name = "Dual (Híbrido)" if qdrant_stats.get("status") == "online" else "Dual (Chroma Fallback)"

        return {
            "total_chunks": total_chunks, 
            "unique_sources": len(all_sources),
            "sources": all_sources,
            "collection_name": self.config.collection_name, 
            "backend": backend_name,
            "details": {
                "chroma": chroma_stats,
                "qdrant": qdrant_stats
            }
        }

    def delete_document_by_name(self, filename: str) -> bool:
        res_chroma = False
        res_qdrant = False
        try:
            res_chroma = self.chroma.delete_document_by_name(filename)
        except: pass
        
        if self._qdrant_online:
            try:
                res_qdrant = self.qdrant.delete_document_by_name(filename)
            except: pass

        return res_chroma or res_qdrant

    def clear_all_data(self) -> None:
        self.chroma.clear_all_data()
        if self._qdrant_online:
            try:
                self.qdrant.clear_all_data()
            except: pass


# ==============================================================================
# 5. Factory Function - MANTÉM ASSINATURA ORIGINAL
# ==============================================================================
def VectorStore(config: Config, max_workers: int = 4) -> BaseVectorStore:
    """
    Factory para criar VectorStore apropriado
    
    Args:
        config: Configuração do sistema
        max_workers: Workers para thread pool (async)
        
    Returns:
        Instância de BaseVectorStore (com suporte sync e async)
    """
    provider = getattr(config, "vector_store_provider", "chroma").lower()
    
    if provider == "dual":
        return DualVectorStore(config, max_workers)
    elif provider == "qdrant":
        return QdrantVectorStoreImp(config, max_workers)
    else:
        return ChromaDBVectorStore(config, max_workers)
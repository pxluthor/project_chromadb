"""
Módulo para gerenciamento do banco vetorial ChromaDB
"""
from pathlib import Path
from typing import List, Dict, Optional
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

from .pdf_extractor import PDFDocument
from .config import Config


class VectorStore:
    """Gerencia o banco vetorial ChromaDB"""
    
    def __init__(self, config: Config):
        """
        Inicializa o VectorStore
        
        Args:
            config: Configuração do sistema
        """
        self.config = config
        
        # Inicializa embeddings
        self.embeddings = OpenAIEmbeddings(
            model=config.embedding_model,
            openai_api_key=config.openai_api_key
        )
        
        # Text splitter para chunking
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.chunk_size,
            chunk_overlap=config.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        # Vectorstore (será inicializado quando necessário)
        self._vectorstore: Optional[Chroma] = None
    
    @property
    def vectorstore(self) -> Chroma:
        """Lazy loading do vectorstore"""
        if self._vectorstore is None:
            self._vectorstore = self._load_or_create_vectorstore()
        return self._vectorstore
    
    def _load_or_create_vectorstore(self) -> Chroma:
        """Carrega ou cria o vectorstore"""
        return Chroma(
            collection_name=self.config.collection_name,
            embedding_function=self.embeddings,
            persist_directory=str(self.config.chroma_dir)
        )
    
    def add_documents(self, pdf_documents: List[PDFDocument]) -> Dict[str, any]:
        """
        Adiciona documentos PDF ao vectorstore
        
        Args:
            pdf_documents: Lista de PDFDocuments
            
        Returns:
            Estatísticas da indexação
        """
        all_chunks = []
        stats = {
            "total_documents": len(pdf_documents),
            "total_pages": 0,
            "total_chunks": 0,
            "documents_processed": []
        }
        
        for pdf_doc in pdf_documents:
            # Cria chunks do documento
            chunks = self._create_chunks(pdf_doc)
            all_chunks.extend(chunks)
            
            stats["total_pages"] += pdf_doc.total_pages
            stats["total_chunks"] += len(chunks)
            stats["documents_processed"].append({
                "filename": pdf_doc.metadata["filename"],
                "pages": pdf_doc.total_pages,
                "chunks": len(chunks)
            })
        
        # Adiciona ao vectorstore
        if all_chunks:
            self.vectorstore.add_documents(all_chunks)
        
        return stats
    
    def _create_chunks(self, pdf_doc: PDFDocument) -> List[Document]:
        """
        Cria chunks de um documento PDF
        
        Args:
            pdf_doc: Documento PDF
            
        Returns:
            Lista de Documents do LangChain
        """
        chunks = []
        
        for page in pdf_doc.pages:
            # Split o texto da página em chunks
            page_chunks = self.text_splitter.split_text(page.text)
            
            # Cria Document para cada chunk
            for i, chunk_text in enumerate(page_chunks):
                metadata = {
                    "source": pdf_doc.metadata["filename"],
                    "filepath": str(pdf_doc.filepath),
                    "page": page.page_number,
                    "chunk_id": i,
                    "title": pdf_doc.metadata["title"],
                    "author": pdf_doc.metadata["author"],
                    "file_hash": pdf_doc.metadata["file_hash"]
                }
                
                doc = Document(
                    page_content=chunk_text,
                    metadata=metadata
                )
                chunks.append(doc)
        
        return chunks
    
    def search(
        self, 
        query: str, 
        k: Optional[int] = None,
        filter_dict: Optional[Dict] = None
    ) -> List[Document]:
        """
        Busca documentos similares
        
        Args:
            query: Query de busca
            k: Número de resultados (usa default_k se None)
            filter_dict: Filtros de metadados
            
        Returns:
            Lista de documentos relevantes
        """
        k = k or self.config.default_k
        
        if filter_dict:
            return self.vectorstore.similarity_search(
                query, 
                k=k,
                filter=filter_dict
            )
        else:
            return self.vectorstore.similarity_search(query, k=k)
    
    def search_with_scores(
        self, 
        query: str, 
        k: Optional[int] = None
    ) -> List[tuple[Document, float]]:
        """
        Busca documentos com scores de similaridade
        
        Args:
            query: Query de busca
            k: Número de resultados
            
        Returns:
            Lista de tuplas (documento, score)
        """
        k = k or self.config.default_k
        return self.vectorstore.similarity_search_with_score(query, k=k)
    
    def delete_collection(self) -> None:
        """Deleta a collection do vectorstore"""
        if self._vectorstore:
            self._vectorstore.delete_collection()
            self._vectorstore = None
    
    def get_collection_stats_old(self) -> Dict[str, any]:
        """
        Retorna estatísticas da collection
        
        Returns:
            Dicionário com estatísticas
        """
        try:
            collection = self.vectorstore._collection
            count = collection.count()
            
            # Pega alguns documentos para extrair metadados únicos
            if count > 0:
                results = collection.get(limit=min(100, count))
                sources = set()
                
                if results and "metadatas" in results:
                    for metadata in results["metadatas"]:
                        if "source" in metadata:
                            sources.add(metadata["source"])
                
                return {
                    "total_chunks": count,
                    "unique_sources": len(sources),
                    "sources": sorted(list(sources)),
                    "collection_name": self.config.collection_name
                }
            else:
                return {
                    "total_chunks": 0,
                    "unique_sources": 0,
                    "sources": [],
                    "collection_name": self.config.collection_name
                }
        except Exception as e:
            return {
                "error": str(e),
                "collection_name": self.config.collection_name
            }
    
    def get_collection_stats(self) -> Dict[str, any]:
        """
        Retorna estatísticas da collection (Versão Corrigida para listar tudo)
        """
        try:
            collection = self.vectorstore._collection
            count = collection.count()
            
            if count > 0:
                # ALTERAÇÃO AQUI: Removemos o limit=min(100, count)
                # Trazemos apenas os metadados de TODOS os chunks para identificar as fontes únicas
                results = collection.get(include=["metadatas"])
                
                sources = set()
                if results and "metadatas" in results:
                    for metadata in results["metadatas"]:
                        if "source" in metadata:
                            sources.add(metadata["source"])
                
                return {
                    "total_chunks": count,
                    "unique_sources": len(sources),
                    "sources": sorted(list(sources)),
                    "collection_name": self.config.collection_name
                }
            else:
                return {
                    "total_chunks": 0,
                    "unique_sources": 0,
                    "sources": [],
                    "collection_name": self.config.collection_name
                }
        except Exception as e:
            return {
                "error": str(e),
                "collection_name": self.config.collection_name
            }

    def clear_all_data(self) -> None:
        """Limpa todos os dados do vectorstore"""
        import shutil
        if self.config.chroma_dir.exists():
            shutil.rmtree(self.config.chroma_dir)
            self.config.chroma_dir.mkdir(parents=True, exist_ok=True)
        self._vectorstore = None

    def delete_document_by_name(self, filename: str) -> bool:
        """
        Remove todos os chunks associados a um nome de arquivo específico.
        Essencial para Exclusão e Atualização (limpeza prévia).
        """
        try:
            # Remove do ChromaDB filtrando pelo metadado 'source'
            self.vectorstore._collection.delete(
                where={"source": filename}
            )
            return True
        except Exception as e:
            print(f"Erro ao deletar documento {filename}: {e}")
            return False
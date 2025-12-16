"""
Configurações centralizadas do sistema PDF RAG
"""
import os
from pathlib import Path
from typing import Optional
from dataclasses import dataclass


@dataclass
class Config:
    """Configurações do sistema"""
    
    # API Keys
    openai_api_key: str
    
    # Modelos
    llm_model: str = "gpt-4o-mini"
    embedding_model: str = "text-embedding-3-small"
    temperature: float = 0.0
    
    # Chunking
    chunk_size: int = 1000
    chunk_overlap: int = 200
    
    # Retrieval
    default_k: int = 6
    search_type: str = "similarity"
    
    # Paths
    project_root: Path = Path(__file__).parent.parent
    data_dir: Path = project_root / "data"
    pdfs_dir: Path = data_dir / "pdfs"
    chroma_dir: Path = data_dir / "chroma_db"
    
    # ChromaDB
    collection_name: str = "pdf_documents"
    
    # Chat
    max_history: int = 10
    
    def __post_init__(self):
        """Cria diretórios necessários"""
        self.pdfs_dir.mkdir(parents=True, exist_ok=True)
        self.chroma_dir.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def from_env(cls) -> "Config":
        """Carrega configurações de variáveis de ambiente"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY não encontrada. "
                "Configure a variável de ambiente ou crie um arquivo .env"
            )
        
        return cls(
            openai_api_key=api_key,
            llm_model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
            embedding_model=os.getenv("EMBEDDING_MODEL", "text-embedding-3-small"),
            temperature=float(os.getenv("TEMPERATURE", "0.0")),
            chunk_size=int(os.getenv("CHUNK_SIZE", "1000")),
            chunk_overlap=int(os.getenv("CHUNK_OVERLAP", "200")),
            default_k=int(os.getenv("DEFAULT_K", "6")),
            collection_name=os.getenv("COLLECTION_NAME", "pdf_documents"),
            max_history=int(os.getenv("MAX_HISTORY", "10"))
        )


def load_config() -> Config:
    """Carrega configurações do ambiente"""
    # Tenta carregar .env se existir
    try:
        from dotenv import load_dotenv
        env_path = Path(__file__).parent.parent / ".env"
        if env_path.exists():
            load_dotenv(env_path)
    except ImportError:
        pass
    
    return Config.from_env()
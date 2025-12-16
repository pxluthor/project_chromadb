"""
Dependências FastAPI para injeção de componentes
"""
from fastapi import Depends
from typing import Annotated

from src.config import Config
from src.vectorstore import VectorStore
from src.rag_engine import RAGEngine
from api.chat_manager import ChatManager


# Instâncias globais (serão inicializadas no lifespan do main.py)
_config: Config = None
_vectorstore: VectorStore = None
_rag_engine: RAGEngine = None
_chat_manager: ChatManager = None


def set_components(config, vectorstore, rag_engine, chat_manager):
    """Define os componentes globais (chamado pelo main.py)"""
    global _config, _vectorstore, _rag_engine, _chat_manager
    _config = config
    _vectorstore = vectorstore
    _rag_engine = rag_engine
    _chat_manager = chat_manager


def get_config() -> Config:
    """Retorna a configuração"""
    if _config is None:
        raise RuntimeError("Config não inicializada. Sistema não está pronto.")
    return _config


def get_vectorstore() -> VectorStore:
    """Retorna o VectorStore"""
    if _vectorstore is None:
        raise RuntimeError("VectorStore não inicializado. Sistema não está pronto.")
    return _vectorstore


def get_rag_engine() -> RAGEngine:
    """Retorna o RAG Engine"""
    if _rag_engine is None:
        raise RuntimeError("RAG Engine não inicializado. Sistema não está pronto.")
    return _rag_engine


def get_chat_manager() -> ChatManager:
    """Retorna o Chat Manager"""
    if _chat_manager is None:
        raise RuntimeError("Chat Manager não inicializado. Sistema não está pronto.")
    return _chat_manager


# Type hints para uso com Depends
ConfigDep = Annotated[Config, Depends(get_config)]
VectorStoreDep = Annotated[VectorStore, Depends(get_vectorstore)]
RAGEngineDep = Annotated[RAGEngine, Depends(get_rag_engine)]
ChatManagerDep = Annotated[ChatManager, Depends(get_chat_manager)]
"""
Gerenciador de sessões de chat para a API
"""
from typing import Dict, List, Optional
from datetime import datetime
from collections import defaultdict

from src.config import Config
from src.vectorstore import VectorStore
from src.rag_engine import RAGEngine


class ChatSession:
    """Representa uma sessão de chat"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.history: List[Dict[str, str]] = []
        self.created_at = datetime.now()
        self.last_activity = datetime.now()
    
    def add_message(self, role: str, content: str) -> None:
        """Adiciona mensagem ao histórico"""
        self.history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        self.last_activity = datetime.now()
    
    def get_history(self, limit: Optional[int] = None) -> List[Dict[str, str]]:
        """Retorna histórico (limitado se especificado)"""
        if limit:
            return self.history[-limit:]
        return self.history
    
    def clear(self) -> None:
        """Limpa o histórico"""
        self.history = []
        self.last_activity = datetime.now()


class ChatManager:
    """Gerencia múltiplas sessões de chat"""
    
    def __init__(
        self,
        config: Config,
        vectorstore: VectorStore,
        rag_engine: RAGEngine,
        max_history_per_session: int = 20
    ):
        self.config = config
        self.vectorstore = vectorstore
        self.rag_engine = rag_engine
        self.max_history_per_session = max_history_per_session
        
        # Armazena sessões ativas
        self.sessions: Dict[str, ChatSession] = {}
    
    def get_or_create_session(self, session_id: str) -> ChatSession:
        """Obtém ou cria uma sessão"""
        if session_id not in self.sessions:
            self.sessions[session_id] = ChatSession(session_id)
        return self.sessions[session_id]
    
    def send_message(
        self,
        session_id: str,
        message: str,
        k: Optional[int] = None
    ) -> Dict[str, any]:
        """
        Envia mensagem e retorna resposta
        
        Args:
            session_id: ID da sessão
            message: Mensagem do usuário
            k: Número de chunks a recuperar
            
        Returns:
            Resposta do assistente com fontes
        """
        session = self.get_or_create_session(session_id)
        
        # Limita histórico
        history = session.get_history(limit=self.max_history_per_session)
        
        # Processa com RAG Engine
        response = self.rag_engine.chat_query(
            question=message,
            chat_history=history,
            k=k
        )
        
        # Adiciona ao histórico
        session.add_message("user", message)
        session.add_message("assistant", response["answer"])
        
        return response
    
    def get_session_history(self, session_id: str) -> List[Dict[str, str]]:
        """Retorna histórico de uma sessão"""
        if session_id not in self.sessions:
            return []
        return self.sessions[session_id].get_history()
    
    def clear_session(self, session_id: str) -> None:
        """Limpa histórico de uma sessão"""
        if session_id in self.sessions:
            self.sessions[session_id].clear()
    
    def delete_session(self, session_id: str) -> None:
        """Remove uma sessão completamente"""
        if session_id in self.sessions:
            del self.sessions[session_id]
    
    def get_active_sessions(self) -> List[str]:
        """Retorna lista de sessões ativas"""
        return list(self.sessions.keys())
    
    def get_session_count(self) -> int:
        """Retorna número de sessões ativas"""
        return len(self.sessions)
    
    def cleanup_inactive_sessions(self, max_age_minutes: int = 60) -> int:
        """
        Remove sessões inativas
        
        Args:
            max_age_minutes: Idade máxima em minutos
            
        Returns:
            Número de sessões removidas
        """
        now = datetime.now()
        to_remove = []
        
        for session_id, session in self.sessions.items():
            age = (now - session.last_activity).total_seconds() / 60
            if age > max_age_minutes:
                to_remove.append(session_id)
        
        for session_id in to_remove:
            del self.sessions[session_id]
        
        return len(to_remove)
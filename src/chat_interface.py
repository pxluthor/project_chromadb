"""
Interface de chat conversacional
"""
from typing import List, Dict, Optional
from datetime import datetime

from .config import Config
from .rag_engine import RAGEngine
from .vectorstore import VectorStore


class ChatInterface:
    """Interface de chat conversacional com RAG"""
    
    def __init__(self, config: Config, vectorstore: VectorStore, rag_engine: RAGEngine):
        """
        Inicializa a interface de chat
        
        Args:
            config: Configuração do sistema
            vectorstore: Instância do VectorStore
            rag_engine: Engine RAG
        """
        self.config = config
        self.vectorstore = vectorstore
        self.rag_engine = rag_engine
        self.chat_history: List[Dict[str, str]] = []
        self.session_start = datetime.now()
    
    def send_message(self, message: str, k: Optional[int] = None) -> Dict[str, any]:
        """
        Envia mensagem e recebe resposta
        
        Args:
            message: Mensagem do usuário
            k: Número de chunks a recuperar
            
        Returns:
            Resposta do assistente
        """
        # Limita histórico ao máximo configurado
        if len(self.chat_history) >= self.config.max_history * 2:
            self.chat_history = self.chat_history[-(self.config.max_history * 2):]
        
        # Processa a mensagem
        response = self.rag_engine.chat_query(
            question=message,
            chat_history=self.chat_history,
            k=k
        )
        
        # Adiciona ao histórico
        self.chat_history.append({
            "role": "user",
            "content": message,
            "timestamp": datetime.now().isoformat()
        })
        
        self.chat_history.append({
            "role": "assistant",
            "content": response["answer"],
            "timestamp": datetime.now().isoformat(),
            "num_sources": response["num_sources"]
        })
        
        return response
    
    def clear_history(self) -> None:
        """Limpa o histórico de conversa"""
        self.chat_history = []
        self.session_start = datetime.now()
    
    def get_history(self) -> List[Dict[str, str]]:
        """Retorna o histórico de conversa"""
        return self.chat_history.copy()
    
    def get_session_info(self) -> Dict[str, any]:
        """Retorna informações da sessão"""
        duration = datetime.now() - self.session_start
        
        return {
            "session_start": self.session_start.isoformat(),
            "duration_seconds": int(duration.total_seconds()),
            "total_messages": len(self.chat_history),
            "user_messages": len([m for m in self.chat_history if m["role"] == "user"]),
            "assistant_messages": len([m for m in self.chat_history if m["role"] == "assistant"])
        }
    
    def format_conversation(self) -> str:
        """Formata a conversa para exibição"""
        lines = []
        lines.append("="*80)
        lines.append("HISTÓRICO DA CONVERSA")
        lines.append("="*80)
        
        for msg in self.chat_history:
            role = "👤 VOCÊ" if msg["role"] == "user" else "🤖 ASSISTENTE"
            timestamp = msg.get("timestamp", "")
            
            lines.append(f"\n{role} ({timestamp}):")
            lines.append(msg["content"])
            
            if msg["role"] == "assistant" and "num_sources" in msg:
                lines.append(f"   └─ Baseado em {msg['num_sources']} fonte(s)")
        
        lines.append("\n" + "="*80)
        return "\n".join(lines)
    
    def export_conversation(self, filepath: str) -> None:
        """
        Exporta conversa para arquivo
        
        Args:
            filepath: Caminho do arquivo de destino
        """
        from pathlib import Path
        import json
        
        export_data = {
            "session_info": self.get_session_info(),
            "vectorstore_stats": self.vectorstore.get_collection_stats(),
            "chat_history": self.chat_history
        }
        
        output_path = Path(filepath)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Conversa exportada para: {output_path}")
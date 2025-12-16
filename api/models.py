from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

# =========================
# Shared Models
# =========================

class MediaItemResponse(BaseModel):
    type: str
    url: str
    title: Optional[str] = None
    description: Optional[str] = None
    thumbnail_url: Optional[str] = None
    duration: Optional[int] = None

class SourceModel(BaseModel):
    """Modelo para representar a fonte de um documento"""
    source: str
    page: Optional[Any] = None
    title: Optional[str] = "N/A"
    excerpt: Optional[str] = None
    chunk_id: Optional[str] = None
    pdf_url: Optional[str] = None
    media: Optional[List[MediaItemResponse]] = None

class ChunkData(BaseModel):
    """Modelo para dados de um chunk na busca"""
    content: str
    metadata: Dict[str, Any]

# =========================
# Request Models
# =========================

class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1, description="A pergunta a ser respondida")
    k: int = Field(default=6, ge=1, le=20, description="Número de chunks a recuperar")
    include_sources: bool = Field(default=True, description="Incluir fontes na resposta")

class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Texto para busca semântica")
    k: int = Field(default=5, ge=1, le=20, description="Número de resultados")
    filter: Optional[Dict[str, Any]] = Field(default=None, description="Filtros de metadados (ex: {'source': 'file.pdf'})")

class ChatRequest(BaseModel):
    session_id: str = Field(..., min_length=1, description="ID único da sessão de chat")
    message: str = Field(..., min_length=1, description="Mensagem do usuário")
    k: int = Field(default=6, ge=1, le=20, description="Número de chunks a recuperar")

# =========================
# Response Models
# =========================

class QueryResponse(BaseModel):
    question: str
    answer: str
    sources: List[SourceModel] = []
    num_sources: int
    media: List[MediaItemResponse] = [] 
    has_media: bool = False

class SearchResponse(BaseModel):
    query: str
    chunks: List[ChunkData]
    total_results: int

class ChatResponse(BaseModel):
    session_id: str
    message: str
    response: str
    sources: List[SourceModel] = []
    num_sources: int
    media: List[MediaItemResponse] = []
    has_media: bool = False
    
class HealthResponse(BaseModel):
    status: str
    components: Dict[str, str]
    total_documents: int

class StatsResponse(BaseModel):
    total_chunks: int
    unique_sources: int
    sources: List[str]
    collection_name: str
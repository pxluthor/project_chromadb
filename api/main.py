"""
API REST para consulta do banco vetorial PDF RAG
Versão sem multimídia (código antigo funcionando)
"""
from fastapi import FastAPI, HTTPException, Depends, status, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from contextlib import asynccontextmanager
import sys, os
import shutil
from pathlib import Path

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.models import (
    QueryRequest,
    QueryResponse,
    SearchRequest,
    SearchResponse,
    HealthResponse,
    StatsResponse,
    ChatRequest,
    ChatResponse
)
from api.dependencies import get_rag_engine, get_vectorstore, get_chat_manager, set_components, get_config
from src.config import load_config
from src.vectorstore import VectorStore
from src.config import Config
from src.rag_engine import RAGEngine
from api.chat_manager import ChatManager
from src.pdf_extractor import PDFExtractor

from api.multimedia_routes import router as multimedia_router # para importar os arquivos de rotas de multimídia
from fastapi.staticfiles import StaticFiles


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia ciclo de vida da aplicação"""
    
    # Startup
    print("🚀 Iniciando PDF RAG API...")
    
    try:
        config = load_config()
        print("✓ Configuração carregada")
        
        vectorstore = VectorStore(config)
        print("✓ VectorStore inicializado")
        
        # RAG Engine SEM multimídia
        rag_engine = RAGEngine(config, vectorstore)
        print("✓ RAG Engine inicializado")
        
        chat_manager = ChatManager(config, vectorstore, rag_engine)
        print("✓ Chat Manager inicializado")
        
        # Define os componentes globais
        set_components(config, vectorstore, rag_engine, chat_manager)
        
        # Verifica se há documentos indexados
        stats = vectorstore.get_collection_stats()
        if stats.get("total_chunks", 0) == 0:
            print("⚠️  ATENÇÃO: Nenhum documento indexado!")
            print("   Execute: python scripts/ingest_pdfs.py data/pdfs/")
        else:
            print(f"✓ {stats['total_chunks']} chunks indexados")
        
        print("✅ API pronta para receber requisições")
        
    except Exception as e:
        print(f"❌ Erro na inicialização: {e}")
        import traceback
        traceback.print_exc()
        raise
    
    yield
    
    # Shutdown
    print("👋 Encerrando API...")


# Cria a aplicação FastAPI
app = FastAPI(
    title="PDF RAG API",
    description="API REST para consulta de documentos PDF usando RAG",
    version="1.0.0",
    lifespan=lifespan
)


pdf_directory = Path("data/pdfs") # Certifique-se que este caminho está correto
pdf_directory.mkdir(parents=True, exist_ok=True)
app.mount("/pdfs", StaticFiles(directory=str(pdf_directory)), name="pdfs")

media_directory = Path("data/media")
media_directory.mkdir(parents=True, exist_ok=True)
app.mount("/media", StaticFiles(directory=str(media_directory)), name="media")

# Configuração CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especifique os domínios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(multimedia_router) # para incluir os arquivos nas rotas de multimídia

# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/", response_model=dict)
async def root():
    """Endpoint raiz"""
    return {
        "message": "PDF RAG API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check(vs: VectorStore = Depends(get_vectorstore)):
    """
    Health check da API
    
    Verifica se todos os componentes estão funcionando
    """
    try:
        stats = vs.get_collection_stats()
        
        return HealthResponse(
            status="healthy",
            components={
                "vectorstore": "ok",
                "rag_engine": "ok",
                "chat_manager": "ok"
            },
            total_documents=stats.get("total_chunks", 0)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Serviço indisponível: {str(e)}"
        )


@app.get("/stats", response_model=StatsResponse)
async def get_stats(vs: VectorStore = Depends(get_vectorstore)):
    """
    Retorna estatísticas do banco vetorial
    
    Informações sobre documentos indexados, chunks, etc.
    """
    try:
        stats = vs.get_collection_stats()
        
        return StatsResponse(
            total_chunks=stats.get("total_chunks", 0),
            unique_sources=stats.get("unique_sources", 0),
            sources=stats.get("sources", []),
            collection_name=stats.get("collection_name", "N/A")
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.post("/query", response_model=QueryResponse)
async def query_documents(
    request: QueryRequest,
    rag: RAGEngine = Depends(get_rag_engine)
):
    """
    Faz uma pergunta e retorna resposta baseada nos documentos
    
    Este é o endpoint principal para agentes de IA consultarem documentos.
    """
    try:
        if not request.question or not request.question.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Pergunta não pode ser vazia"
            )
        
        result = rag.query(
            question=request.question,
            k=request.k,
            include_sources=request.include_sources
        )
        
        return QueryResponse(
            question=result["question"],
            answer=result["answer"],
            sources=result.get("sources", []),
            num_sources=result["num_sources"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar query: {str(e)}"
        )




@app.post("/search", response_model=SearchResponse)
async def search_documents(
    request: SearchRequest,
    vs: VectorStore = Depends(get_vectorstore)
):
    """
    Busca chunks similares sem gerar resposta
    """
    try:
        if not request.query or not request.query.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Query não pode ser vazia"
            )
        
        # Busca com ou sem filtros
        if request.filter:
            results = vs.search(
                request.query,
                k=request.k,
                filter_dict=request.filter
            )
        else:
            results = vs.search(request.query, k=request.k)
        
        # Formata resultados
        chunks = []
        for doc in results:
            # CORREÇÃO AQUI:
            # Antes: Criávamos um dicionário manual que excluía o _debug_origin
            # Agora: Passamos o doc.metadata completo, que contém a origem injetada
            chunks.append({
                "content": doc.page_content,
                "metadata": doc.metadata 
            })
        
        return SearchResponse(
            query=request.query,
            chunks=chunks,
            total_results=len(chunks)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar documentos: {str(e)}"
        )


@app.post("/chat", response_model=ChatResponse)
async def chat_with_documents(
    request: ChatRequest,
    chat_mgr: ChatManager = Depends(get_chat_manager)
):
    """
    Chat conversacional com histórico
    
    Permite conversas contínuas mantendo contexto.
    """
    try:
        if not request.message or not request.message.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mensagem não pode ser vazia"
            )
        
        response = chat_mgr.send_message(
            session_id=request.session_id,
            message=request.message,
            k=request.k
        )
        
        return ChatResponse(
            session_id=request.session_id,
            message=request.message,
            response=response["answer"],
            sources=response.get("sources", []),
            num_sources=response["num_sources"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro no chat: {str(e)}"
        )


@app.delete("/chat/{session_id}")
async def clear_chat_session(
    session_id: str,
    chat_mgr: ChatManager = Depends(get_chat_manager)
):
    """
    Limpa o histórico de uma sessão de chat
    """
    try:
        chat_mgr.clear_session(session_id)
        return {"message": f"Sessão {session_id} limpa com sucesso"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao limpar sessão: {str(e)}"
        )


@app.get("/chat/{session_id}/history")
async def get_chat_history(
    session_id: str,
    chat_mgr: ChatManager = Depends(get_chat_manager)
):
    """
    Retorna o histórico de uma sessão de chat
    """
    try:
        history = chat_mgr.get_session_history(session_id)
        return {
            "session_id": session_id,
            "history": history,
            "total_messages": len(history)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao recuperar histórico: {str(e)}"
        )


@app.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    vs: VectorStore = Depends(get_vectorstore),
    config: Config = Depends(get_config)
):
    """
    Rota Unificada: Cria Novo ou Atualiza Existente.
    Se o arquivo já existir, ele é substituído (reindexado).
    """
    try:
        filename = file.filename
        file_path = config.pdfs_dir / filename
        
        # 1. Tenta limpar versão anterior (Lógica de Atualização)
        # Se não existir, não faz mal, o método apenas não encontra nada.
        vs.delete_document_by_name(filename)
        
        # 2. Salva o novo arquivo físico
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # 3. Processa e Indexa
        extractor = PDFExtractor()
        try:
            doc = extractor.extract_from_file(file_path)
            stats = vs.add_documents([doc])
            
            return {
                "message": f"Arquivo '{filename}' processado com sucesso (Adicionado/Atualizado)",
                "stats": stats
            }
        except Exception as e:
            # Rollback: apaga o arquivo se a leitura falhar
            if file_path.exists():
                os.remove(file_path)
            raise HTTPException(status_code=400, detail=f"Erro ao processar PDF: {str(e)}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/documents/{filename}")
async def delete_document(
    filename: str,
    vs: VectorStore = Depends(get_vectorstore),
    config: Config = Depends(get_config)
):
    """
    Rota de Exclusão: Remove embeddings e arquivo físico.
    """
    try:
        # 1. Remove do ChromaDB
        success = vs.delete_document_by_name(filename)
        
        # 2. Remove do disco
        file_path = config.pdfs_dir / filename
        if file_path.exists():
            os.remove(file_path)
            
        if not success:
            raise HTTPException(status_code=500, detail="Erro ao remover do banco de dados")
            
        return {"message": f"Documento '{filename}' excluído permanentemente"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/documents/{filename}/view")
async def view_document(
    filename: str,
    config: Config = Depends(get_config)
):
    """
    Serve o arquivo PDF para visualização no navegador.
    """
    file_path = config.pdfs_dir / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")
    
    # Retorna o arquivo com o tipo MIME correto para o navegador abrir
    return FileResponse(path=file_path, media_type="application/pdf", filename=filename)

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handler para HTTPException"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handler para exceções gerais"""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Erro interno do servidor",
            "detail": str(exc),
            "status_code": 500
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8005,
        reload=True,
        log_level="debug"
    )

# uvicorn api.main:app --host 0.0.0.0 --port 8005 --reload --log-level debug